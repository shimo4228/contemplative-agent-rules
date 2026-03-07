"""Main orchestrator for the Contemplative Moltbook Agent."""

import enum
import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Set

from .auth import check_claim_status, load_credentials, register_agent
from .client import MoltbookClient, MoltbookClientError
from .config import FORBIDDEN_SUBSTRING_PATTERNS, FORBIDDEN_WORD_PATTERNS, MAX_POST_LENGTH, VALID_ID_PATTERN
from .content import ContentManager
from .llm import extract_topics, generate_post_title, generate_reply, score_relevance
from .memory import MemoryStore
from .scheduler import Scheduler
from .verification import (
    VerificationTracker,
    solve_challenge,
    submit_verification,
)

logger = logging.getLogger(__name__)

ACTIVITY_LOG_PATH = Path.home() / ".config" / "moltbook" / "activity.jsonl"
RELEVANCE_THRESHOLD = 0.5
KNOWN_AGENT_THRESHOLD = 0.3


def _append_activity(action: str, post_id: str, content: str, **extra: str) -> None:
    """Append a single activity record to the JSONL log."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "post_id": post_id,
        "content": content,
        **extra,
    }
    try:
        ACTIVITY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with ACTIVITY_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:
        logger.warning("Failed to write activity log: %s", exc)


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
        memory: Optional[MemoryStore] = None,
    ) -> None:
        self._autonomy = autonomy
        self._content = ContentManager()
        self._verification = VerificationTracker()
        self._client: Optional[MoltbookClient] = None
        self._scheduler: Optional[Scheduler] = None
        self._actions_taken: List[str] = []
        self._commented_posts: Set[str] = set()
        self._rate_limited: bool = False
        self._memory = memory or MemoryStore()
        self._memory.load()

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
        for pattern in FORBIDDEN_SUBSTRING_PATTERNS:
            if pattern.lower() in content_lower:
                logger.warning("Content contains forbidden pattern: %s", pattern)
                return False
        for pattern in FORBIDDEN_WORD_PATTERNS:
            if re.search(r"\b" + re.escape(pattern) + r"\b", content, re.IGNORECASE):
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
        if not VALID_ID_PATTERN.match(post_id):
            logger.warning("Invalid post_id format: %s", post_id[:50])
            return False

        # Skip posts we already commented on this session
        if post_id in self._commented_posts:
            logger.debug("Already commented on %s, skipping", post_id)
            return False

        score = score_relevance(post_text)
        # Lower threshold for agents we've previously interacted with
        author_id = (post.get("author") or {}).get("id", "")
        threshold = (
            KNOWN_AGENT_THRESHOLD
            if author_id and self._memory.has_interacted_with(author_id)
            else RELEVANCE_THRESHOLD
        )
        if score < threshold:
            logger.debug("Post %s relevance %.2f below threshold %.2f", post_id, score, threshold)
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
            logger.info(">> Comment on %s:\n%s", post_id[:12], comment)
            _append_activity("comment", post_id, comment, relevance=f"{score:.2f}")
            # Record interaction in memory
            author = post.get("author") or {}
            agent_name = author.get("name", "unknown")
            agent_id = author.get("id", "unknown")
            self._memory.record_interaction(
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_id=agent_id,
                agent_name=agent_name,
                post_id=post_id,
                direction="sent",
                content=comment,
                interaction_type="comment",
            )
            return True
        except MoltbookClientError as exc:
            logger.error("Failed to comment on %s: %s", post_id, exc)
            if exc.status_code == 429:
                self._rate_limited = True
            return False

    def _auto_follow(self, client: MoltbookClient) -> None:
        """Follow agents we've interacted with frequently."""
        candidates = self._memory.get_agents_to_follow(min_interactions=3)
        for agent_id, agent_name in candidates:
            if client.follow_agent(agent_name):
                self._memory.record_follow(agent_name)
                self._actions_taken.append(f"Followed {agent_name}")
                _append_activity("follow", "", "", target_agent=agent_name)

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

        self._auto_follow(client)

        while time.time() < end_time:
            if self._verification.should_stop:
                logger.error("Verification failure limit reached. Ending session.")
                break

            if self._rate_limited:
                logger.info("Rate limited by server. Ending session early.")
                break

            try:
                self._run_reply_cycle(client, scheduler, end_time)
                self._run_feed_cycle(client, scheduler, end_time)
                self._run_post_cycle(client, scheduler, end_time)
            except Exception:
                logger.exception("Error in session cycle, continuing...")

            # Wait before next cycle
            wait = min(
                scheduler.seconds_until_comment(),
                scheduler.seconds_until_post(),
                60.0,
            )
            if wait > 0 and time.time() + wait < end_time:
                logger.info("Next cycle in %.0fs", wait)
                time.sleep(wait)

        self._memory.save()
        self._print_report()
        return list(self._actions_taken)

    def _run_reply_cycle(
        self,
        client: MoltbookClient,
        scheduler: Scheduler,
        end_time: float,
    ) -> None:
        """Check for and respond to replies on our posts/comments."""
        if not scheduler.can_comment():
            return

        notifications = client.get_notifications()
        for notif in notifications:
            if time.time() >= end_time or self._rate_limited:
                break
            if not scheduler.can_comment():
                break

            notif_type = notif.get("type", "")
            if notif_type not in ("reply", "comment"):
                continue

            post_id = notif.get("post_id", "")
            if not post_id or not VALID_ID_PATTERN.match(post_id):
                continue

            # Skip if already handled this session
            reply_key = f"reply:{post_id}:{notif.get('id', '')}"
            if reply_key in self._commented_posts:
                continue

            their_content = notif.get("content", "")
            original_post = notif.get("post_content", "")
            if not their_content:
                continue

            # Get conversation history with this agent
            replier_id = notif.get("agent_id", "unknown")
            replier_name = notif.get("agent_name", "unknown")
            history = self._memory.get_history_with(replier_id, limit=5)
            history_summaries = [h.content_summary for h in history]

            reply = generate_reply(
                original_post=original_post,
                their_comment=their_content,
                conversation_history=history_summaries,
            )
            if reply is None:
                continue

            if not self._confirm_action(
                f"Reply to {replier_name} on post {post_id}", reply
            ):
                continue

            # Record the incoming reply first (chronological order)
            self._memory.record_interaction(
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_id=replier_id,
                agent_name=replier_name,
                post_id=post_id,
                direction="received",
                content=their_content,
                interaction_type="reply",
            )

            scheduler.wait_for_comment()
            try:
                client.post(
                    f"/posts/{post_id}/comments",
                    json={"content": reply},
                )
                scheduler.record_comment()
                self._commented_posts.add(reply_key)
                self._actions_taken.append(
                    f"Replied to {replier_name} on {post_id}"
                )
                logger.info(">> Reply to %s on %s:\n%s", replier_name, post_id[:12], reply)
                _append_activity("reply", post_id, reply, target_agent=replier_name)
                self._memory.record_interaction(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    agent_id=replier_id,
                    agent_name=replier_name,
                    post_id=post_id,
                    direction="sent",
                    content=reply,
                    interaction_type="reply",
                )
            except MoltbookClientError as exc:
                logger.error("Failed to reply on %s: %s", post_id, exc)
                if exc.status_code == 429:
                    self._rate_limited = True

    def _run_feed_cycle(
        self,
        client: MoltbookClient,
        scheduler: Scheduler,
        end_time: float,
    ) -> None:
        """Fetch and engage with posts from the feed."""
        posts = self._fetch_feed()
        for post in posts:
            if time.time() >= end_time or self._rate_limited:
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
        """Post new content if rate limit allows."""
        if not scheduler.can_post():
            return

        self._run_dynamic_post(client, scheduler)

    def _run_dynamic_post(
        self,
        client: MoltbookClient,
        scheduler: Scheduler,
    ) -> None:
        """Generate and publish a post based on current feed topics."""
        posts = self._fetch_feed()
        topics = extract_topics(posts)
        if not topics:
            return

        content = self._content.create_cooperation_post(topics)
        if content is None:
            return

        title = generate_post_title(topics) or f"Contemplative Note — {topics[:40]}"

        if not self._confirm_action(f"Dynamic Post: {title}", content):
            return

        # Re-check rate limit right before posting (another session may have posted)
        if not scheduler.can_post():
            logger.info("Post rate limit hit after content generation (concurrent session?)")
            return

        scheduler.wait_for_post()
        try:
            client.post(
                "/posts",
                json={
                    "title": title,
                    "content": content,
                    "submolt": "alignment",
                },
            )
            scheduler.record_post()
            self._actions_taken.append(f"Posted: {title}")
            logger.info(">> New post [%s]:\n%s", title, content)
            _append_activity("post", "", content, title=title)
        except MoltbookClientError as exc:
            logger.error("Failed to post dynamic content: %s", exc)

    def _print_report(self) -> None:
        """Print session summary."""
        print("\n=== Session Report ===")
        print(f"Actions taken: {len(self._actions_taken)}")
        for action in self._actions_taken:
            print(f"  - {action}")
        if self._scheduler:
            print(f"Comments remaining today: {self._scheduler.comments_remaining_today}")
        print(f"Comment:Post ratio: {self._content.comment_to_post_ratio:.1f}")
        print(f"Memory: {self._memory.interaction_count()} interactions, "
              f"{self._memory.unique_agent_count()} agents known")
        print("======================\n")
