"""Persistent conversation memory for cross-session context."""

from __future__ import annotations

import json
import logging
import os
import stat
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple

logger = logging.getLogger(__name__)

MEMORY_PATH = Path.home() / ".config" / "moltbook" / "memory.json"
MAX_INTERACTIONS = 1000
MAX_POST_HISTORY = 50
MAX_INSIGHTS = 30
SUMMARY_MAX_LENGTH = 200


@dataclass(frozen=True)
class Interaction:
    """Record of a single interaction with another agent."""

    timestamp: str
    agent_id: str
    agent_name: str
    post_id: str
    direction: Literal["sent", "received"]
    content_summary: str
    interaction_type: Literal["comment", "reply", "post"]


@dataclass(frozen=True)
class PostRecord:
    """Record of a post made by this agent."""

    timestamp: str
    post_id: str
    title: str
    topic_summary: str  # 1-line summary of what the post was about
    content_hash: str  # first 16 chars of SHA-256


@dataclass(frozen=True)
class Insight:
    """Session-end reflection."""

    timestamp: str
    observation: str
    insight_type: str  # "topic_saturation", "engagement_low", "new_direction", etc.


def _truncate(text: str, max_length: int = SUMMARY_MAX_LENGTH) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


class MemoryStore:
    """Manages persistent conversation memory as JSON."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self._path = path or MEMORY_PATH
        self._interactions: List[Interaction] = []
        self._known_agents: Dict[str, str] = {}  # agent_id -> name
        self._followed_agents: set[str] = set()  # agent names already followed
        self._post_history: List[PostRecord] = []
        self._insights: List[Insight] = []

    @property
    def interactions(self) -> Tuple[Interaction, ...]:
        return tuple(self._interactions)

    @property
    def known_agents(self) -> Dict[str, str]:
        return dict(self._known_agents)

    def load(self) -> None:
        """Load memory from disk. No-op if file doesn't exist."""
        if not self._path.exists():
            logger.debug("No memory file at %s", self._path)
            return

        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to load memory: %s", exc)
            return

        for item in raw.get("interactions", []):
            try:
                self._interactions.append(Interaction(**item))
            except TypeError:
                logger.warning("Skipping malformed interaction: %s", item)

        self._known_agents = raw.get("known_agents", {})
        self._followed_agents = set(raw.get("followed_agents", []))

        for item in raw.get("post_history", []):
            try:
                self._post_history.append(PostRecord(**item))
            except TypeError:
                logger.warning("Skipping malformed post record: %s", item)

        for item in raw.get("insights", []):
            try:
                self._insights.append(Insight(**item))
            except TypeError:
                logger.warning("Skipping malformed insight: %s", item)

        logger.info(
            "Loaded memory: %d interactions, %d known agents, "
            "%d post records, %d insights",
            len(self._interactions),
            len(self._known_agents),
            len(self._post_history),
            len(self._insights),
        )

    def save(self) -> None:
        """Persist memory to disk with restricted permissions."""
        self._path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "interactions": [asdict(i) for i in self._interactions],
            "known_agents": self._known_agents,
            "followed_agents": sorted(self._followed_agents),
            "post_history": [asdict(p) for p in self._post_history],
            "insights": [asdict(i) for i in self._insights],
        }

        self._path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        os.chmod(self._path, stat.S_IRUSR | stat.S_IWUSR)  # 0600

    def record_interaction(
        self,
        timestamp: str,
        agent_id: str,
        agent_name: str,
        post_id: str,
        direction: Literal["sent", "received"],
        content: str,
        interaction_type: Literal["comment", "reply", "post"],
    ) -> Interaction:
        """Record an interaction and update known agents."""
        interaction = Interaction(
            timestamp=timestamp,
            agent_id=agent_id,
            agent_name=agent_name,
            post_id=post_id,
            direction=direction,
            content_summary=_truncate(content),
            interaction_type=interaction_type,
        )
        self._interactions.append(interaction)
        self._known_agents[agent_id] = agent_name

        # Trim to max size
        if len(self._interactions) > MAX_INTERACTIONS:
            self._interactions = self._interactions[-MAX_INTERACTIONS:]

        return interaction

    def get_history_with(
        self, agent_id: str, limit: int = 10
    ) -> List[Interaction]:
        """Get recent interactions with a specific agent."""
        matches = [i for i in self._interactions if i.agent_id == agent_id]
        return matches[-limit:]

    def get_recent(self, limit: int = 50) -> List[Interaction]:
        """Get most recent interactions across all agents."""
        return self._interactions[-limit:]

    def has_interacted_with(self, agent_id: str) -> bool:
        """Check if we have any history with this agent."""
        return any(i.agent_id == agent_id for i in self._interactions)

    def unique_agent_count(self) -> int:
        """Count unique agents we've interacted with."""
        return len(self._known_agents)

    def interaction_count(self) -> int:
        """Total number of recorded interactions."""
        return len(self._interactions)

    def interaction_count_with(self, agent_id: str) -> int:
        """Count total interactions with a specific agent."""
        return sum(1 for i in self._interactions if i.agent_id == agent_id)

    def is_followed(self, agent_name: str) -> bool:
        """Check if we've already followed this agent."""
        return agent_name in self._followed_agents

    def record_follow(self, agent_name: str) -> None:
        """Mark an agent as followed."""
        self._followed_agents.add(agent_name)

    def get_agents_to_follow(self, min_interactions: int = 3) -> List[Tuple[str, str]]:
        """Return (agent_id, agent_name) pairs for agents we interact with
        frequently but haven't followed yet."""
        candidates = []
        for agent_id, agent_name in self._known_agents.items():
            if self.is_followed(agent_name):
                continue
            if self.interaction_count_with(agent_id) >= min_interactions:
                candidates.append((agent_id, agent_name))
        return candidates

    def record_post(
        self,
        timestamp: str,
        post_id: str,
        title: str,
        topic_summary: str,
        content_hash: str,
    ) -> PostRecord:
        """Record a post made by this agent."""
        record = PostRecord(
            timestamp=timestamp,
            post_id=post_id,
            title=title,
            topic_summary=_truncate(topic_summary, 100),
            content_hash=content_hash[:16],
        )
        self._post_history.append(record)

        if len(self._post_history) > MAX_POST_HISTORY:
            self._post_history = self._post_history[-MAX_POST_HISTORY:]

        return record

    def record_insight(
        self,
        timestamp: str,
        observation: str,
        insight_type: str,
    ) -> Insight:
        """Record a session-end insight."""
        insight = Insight(
            timestamp=timestamp,
            observation=_truncate(observation),
            insight_type=insight_type,
        )
        self._insights.append(insight)

        if len(self._insights) > MAX_INSIGHTS:
            self._insights = self._insights[-MAX_INSIGHTS:]

        return insight

    def get_recent_post_topics(self, limit: int = 5) -> List[str]:
        """Return topic_summaries of recent posts."""
        return [p.topic_summary for p in self._post_history[-limit:]]

    def get_recent_insights(self, limit: int = 3) -> List[str]:
        """Return observation strings of recent insights."""
        return [i.observation for i in self._insights[-limit:]]
