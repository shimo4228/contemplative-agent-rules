"""Persistent conversation memory for cross-session context."""

from __future__ import annotations

import json
import logging
import os
import stat
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

MEMORY_PATH = Path.home() / ".config" / "moltbook" / "memory.json"
MAX_INTERACTIONS = 1000
SUMMARY_MAX_LENGTH = 200


@dataclass(frozen=True)
class Interaction:
    """Record of a single interaction with another agent."""

    timestamp: str
    agent_id: str
    agent_name: str
    post_id: str
    direction: str  # "sent" | "received"
    content_summary: str
    interaction_type: str  # "comment" | "reply" | "post"


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
        logger.info(
            "Loaded memory: %d interactions, %d known agents",
            len(self._interactions),
            len(self._known_agents),
        )

    def save(self) -> None:
        """Persist memory to disk with restricted permissions."""
        self._path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "interactions": [asdict(i) for i in self._interactions],
            "known_agents": self._known_agents,
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
        direction: str,
        content: str,
        interaction_type: str,
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
