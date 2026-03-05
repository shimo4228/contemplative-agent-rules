"""Main orchestrator for the Contemplative Moltbook Agent."""

import enum
import logging
import re
import time
from typing import List, Optional, Set

from .auth import check_claim_status, load_credentials, register_agent
from .client import MoltbookClient, MoltbookClientError
from .config import FORBIDDEN_PATTERNS, MAX_POST_LENGTH
from .content import ContentManager
from .llm import score_relevance
from .scheduler import Scheduler
from .verification import (
    VerificationTracker,
    solve_challenge,
    submit_verification,
)

logger = logging.getLogger(__name__)

RELEVANCE_THRESHOLD = 0.5
_VALID_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


class AutonomyLevel(str, enum.Enum):
    APPROVE = "approve"
    GUARDED = "guarded"
    AUTO = "auto"


class Agent:
    """Contemplative Moltbook Agent orchestrator.

    Manages the autonomous loop: read feed -> judge relevance ->
    comment/post -> respect rate limits -> report.
    """

    def __init__(
        self,
        autonomy: AutonomyLevel = AutonomyLevel.APPROVE,
    ) -> None:
        self._autonomy = autonomy
        self._content = ContentManager()
        self._verification = VerificationTracker()
        self._client: Optional[MoltbookClient] = None
        self._scheduler: Optional[Scheduler] = None
        self._actions_taken: List[str] = []
        self._commented_posts: Set[str] = set()

    def _ensure_client(self) -> MoltbookClient:
        if self._client is not None:
            return self._client

        api_key = load_credentials()
        if api_key is None:
            raise RuntimeError(
                "No API key found. Run 'contemplative-moltbook register' first."
            )
        self._client = MoltbookClient(api_key)
        self._scheduler = Scheduler()
        return self._client

    def _get_scheduler(self) -> Scheduler:
        """Return scheduler, raising if not initialized."""
        if self._scheduler is None:
            raise RuntimeError("Scheduler not initialized. Call _ensure_client() first.")
        return self._scheduler

    @staticmethod
    def _passes_content_filter(content: str) -> bool:
        """Check content against safety filters for GUARDED mode.

        Returns True if content passes all filters.
        """
        if len(content) > MAX_POST_LENGTH:
            logger.warning("Content exceeds max length (%d > %d)", len(content), MAX_POST_LENGTH)
            return False
        content_lower = content.lower()
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.lower() in content_lower:
                logger.warning("Content contains forbidden pattern: %s", pattern)
                return False
        if not content.strip():
            logger.warning("Content is empty or whitespace-only")
            return False
        return True

    def _confirm_action(self, description: str, content: str) -> bool:
        """Ask for user confirmation based on autonomy level."""
        if self._autonomy is AutonomyLevel.AUTO:
            return True
        if self._autonomy is AutonomyLevel.GUARDED:
            if not self._passes_content_filter(content):
                logger.info("GUARDED mode: content rejected by filter for: %s", description)
                return False
            return True

        # APPROVE mode: interactive confirmation
        print(f"\n--- {description} ---")
        print(content[:500])
        if len(content) > 500:
            print(f"... ({len(content)} chars total)")
        print("---")
        response = input("Post this? [y/N]: ").strip().lower()
        return response == "y"

    def do_register(self) -> dict:
        """Register a new agent on Moltbook."""
        client = MoltbookClient(api_key=None)
        result = register_agent(client)
        claim_url = result.get("claim_url", "")
        if claim_url:
            print(f"Claim your agent at: {claim_url}")
        return result

    def do_status(self) -> dict:
        """Check current agent status."""
        client = self._ensure_client()
        return check_claim_status(client)

    def do_introduce(self) -> Optional[str]:
        """Post the introduction template."""
        client = self._ensure_client()
        scheduler = self._get_scheduler()

        content = self._content.get_introduction()
        if content is None:
            print("Introduction already posted.")
            return None

        if not self._confirm_action("Introduction Post", content):
            print("Skipped.")
            return None

        scheduler.wait_for_post()
        try:
            resp = client.post(
                "/posts",
                json={
                    "title": "Introducing Contemplative Agent",
                    "content": content,
                    "submolt": "alignment",
                },
            )
            scheduler.record_post()
            self._actions_taken.append("Posted introduction")
            result = resp.json()
            print(f"Introduction posted. ID: {result.get('id', 'unknown')}")
            return result.get("id")
        except MoltbookClientError as exc:
            logger.error("Failed to post introduction: %s", exc)
            return None

    def do_solve(self, text: str) -> Optional[str]:
        """Solve a verification challenge (for testing)."""
        answer = solve_challenge(text)
        if answer:
            print(f"Answer: {answer}")
        else:
            print("Failed to solve challenge.")
        return answer

    def _fetch_feed(self) -> List[dict]:
        """Fetch recent posts from the global feed."""
        client = self._ensure_client()
        try:
            resp = client.get("/feed")
            return resp.json().get("posts", [])
        except MoltbookClientError as exc:
            logger.warning("Failed to fetch feed: %s", exc)
            return []

    def _handle_verification(self, challenge: dict) -> bool:
        """Solve and submit a verification challenge."""
        if self._verification.should_stop:
            logger.error("Too many verification failures. Stopping.")
            return False

        challenge_text = challenge.get("text", "")
        challenge_id = challenge.get("id", "")

        answer = solve_challenge(challenge_text)
        if answer is None:
            self._verification.record_failure()
            return False

        client = self._ensure_client()
        try:
            result = submit_verification(client, challenge_id, answer)
            if result.get("success"):
                self._verification.record_success()
                return True
            self._verification.record_failure()
            return False
        except MoltbookClientError as exc:
            logger.error("Verification submission failed: %s", exc)
            self._verification.record_failure()
            return False

    def _engage_with_post(self, post: dict) -> bool:
        """Score and potentially comment on a post."""
        scheduler = self._get_scheduler()
        client = self._ensure_client()

        post_text = post.get("content", "")
        post_id = post.get("id", "")
        if not post_text or not post_id:
            return False

        # Validate post_id to prevent path traversal
        if not _VALID_ID_PATTERN.match(post_id):
            logger.warning("Invalid post_id format: %s", post_id[:50])
            return False

        # Skip posts we already commented on this session
        if post_id in self._commented_posts:
            logger.debug("Already commented on %s, skipping", post_id)
            return False

        score = score_relevance(post_text)
        if score < RELEVANCE_THRESHOLD:
            logger.debug("Post %s relevance %.2f below threshold", post_id, score)
            return False

        if not scheduler.can_comment():
            logger.info("Comment rate limit reached")
            return False

        comment = self._content.create_comment(post_text)
        if comment is None:
            return False

        if not self._confirm_action(
            f"Comment on post {post_id} (relevance: {score:.2f})", comment
        ):
            return False

        scheduler.wait_for_comment()
        try:
            client.post(
                f"/posts/{post_id}/comments",
                json={"content": comment},
            )
            scheduler.record_comment()
            self._commented_posts.add(post_id)
            self._actions_taken.append(
                f"Commented on {post_id} (relevance: {score:.2f})"
            )
            return True
        except MoltbookClientError as exc:
            logger.error("Failed to comment on %s: %s", post_id, exc)
            return False

    def run_session(self, duration_minutes: int = 60) -> List[str]:
        """Run an autonomous engagement session."""
        client = self._ensure_client()
        scheduler = self._get_scheduler()

        end_time = time.time() + (duration_minutes * 60)
        self._actions_taken = []

        logger.info(
            "Starting %d-minute session (autonomy: %s)",
            duration_minutes,
            self._autonomy.value,
        )

        while time.time() < end_time:
            if self._verification.should_stop:
                logger.error("Verification failure limit reached. Ending session.")
                break

            self._run_feed_cycle(client, scheduler, end_time)
            self._run_post_cycle(client, scheduler, end_time)

            # Wait before next cycle
            wait = min(
                scheduler.seconds_until_comment(),
                scheduler.seconds_until_post(),
                60.0,
            )
            if wait > 0 and time.time() + wait < end_time:
                logger.info("Next cycle in %.0fs", wait)
                time.sleep(wait)

        self._print_report()
        return list(self._actions_taken)

    def _run_feed_cycle(
        self,
        client: MoltbookClient,
        scheduler: Scheduler,
        end_time: float,
    ) -> None:
        """Fetch and engage with posts from the feed."""
        posts = self._fetch_feed()
        for post in posts:
            if time.time() >= end_time:
                break
            challenge = post.get("verification_challenge")
            if challenge:
                self._handle_verification(challenge)
                continue
            self._engage_with_post(post)

    def _run_post_cycle(
        self,
        client: MoltbookClient,
        scheduler: Scheduler,
        end_time: float,
    ) -> None:
        """Post new axiom content if rate limit allows."""
        if not scheduler.can_post():
            return
        for axiom in self._content.get_axiom_names():
            content = self._content.get_axiom_post(axiom)
            if content is None:
                continue
            if not self._confirm_action(f"Axiom Post: {axiom}", content):
                continue
            scheduler.wait_for_post()
            try:
                title = f"Deep Dive: {axiom.replace('_', ' ').title()}"
                client.post(
                    "/posts",
                    json={"title": title, "content": content, "submolt": "alignment"},
                )
                scheduler.record_post()
                self._actions_taken.append(f"Posted axiom: {axiom}")
            except MoltbookClientError as exc:
                logger.error("Failed to post %s: %s", axiom, exc)
            break  # Only one post per cycle

    def _print_report(self) -> None:
        """Print session summary."""
        print("\n=== Session Report ===")
        print(f"Actions taken: {len(self._actions_taken)}")
        for action in self._actions_taken:
            print(f"  - {action}")
        if self._scheduler:
            print(f"Comments remaining today: {self._scheduler.comments_remaining_today}")
        print(f"Comment:Post ratio: {self._content.comment_to_post_ratio:.1f}")
        print("======================\n")
