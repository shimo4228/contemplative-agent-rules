"""Constants and configuration for the Moltbook agent."""

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


BASE_URL = "https://www.moltbook.com/api/v1"
ALLOWED_DOMAIN = "www.moltbook.com"

CREDENTIALS_PATH = Path.home() / ".config" / "moltbook" / "credentials.json"
RATE_STATE_PATH = Path.home() / ".config" / "moltbook" / "rate_state.json"

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:7b-instruct-q4_K_M"

GITHUB_REPO_URL = "https://github.com/shimo4228/contemplative-agent-rules"

TARGET_SUBMOLTS: Tuple[str, ...] = (
    "alignment",
    "aisafety",
    "cooperation",
    "philosophy",
)

MAX_VERIFICATION_FAILURES = 7
MAX_RETRY_ON_429 = 3
CONNECT_TIMEOUT = 30
READ_TIMEOUT = 60

MAX_POST_LENGTH = 5000
MAX_COMMENT_LENGTH = 2000
FORBIDDEN_SUBSTRING_PATTERNS: Tuple[str, ...] = (
    "api_key",
    "api-key",
    "apikey",
    "Bearer ",
    "auth_token",
    "access_token",
)
FORBIDDEN_WORD_PATTERNS: Tuple[str, ...] = (
    "password",
    "secret",
)
# Combined for backward compatibility
FORBIDDEN_PATTERNS: Tuple[str, ...] = FORBIDDEN_SUBSTRING_PATTERNS + FORBIDDEN_WORD_PATTERNS


@dataclass(frozen=True)
class RateLimits:
    """Rate limits for Moltbook API actions."""

    read_per_minute: int = 60
    write_per_minute: int = 30
    post_interval_seconds: int = 1800  # 1 per 30 min
    comment_interval_seconds: int = 20
    comments_per_day: int = 50


@dataclass(frozen=True)
class NewAgentRateLimits:
    """Stricter rate limits for agents less than 24h old."""

    post_interval_seconds: int = 7200  # 1 per 2h
    comment_interval_seconds: int = 60
    comments_per_day: int = 20


RATE_LIMITS = RateLimits()
NEW_AGENT_RATE_LIMITS = NewAgentRateLimits()
