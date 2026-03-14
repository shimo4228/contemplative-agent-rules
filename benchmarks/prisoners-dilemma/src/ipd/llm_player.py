"""LLM-based player for the Iterated Prisoner's Dilemma."""

from __future__ import annotations

import json
import logging
import os
import re
import warnings
from enum import Enum
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests

from .game import Move

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen3.5:9b"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-4o-mini"
LOCALHOST_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})

_PROMPTS_DIR = Path(__file__).resolve().parents[4] / "prompts"
CONTEMPLATIVE_PROMPT_PATH = _PROMPTS_DIR / "custom.md"
PAPER_FAITHFUL_PROMPT_PATH = _PROMPTS_DIR / "paper-faithful.md"

GAME_SYSTEM_PROMPT = """\
You are playing the Iterated Prisoner's Dilemma.

Each round, you choose COOPERATE or DEFECT.
Payoffs: Both cooperate = 3,3. Both defect = 1,1. \
You cooperate, they defect = 0,5. You defect, they cooperate = 5,0.

You will play multiple rounds against the same opponent. \
Your goal is to maximize your total score across all rounds.

IMPORTANT: Respond with ONLY the word "COOPERATE" or "DEFECT". \
No explanation, no other text.\
"""


class PromptVariant(str, Enum):
    """Prompt injection modes for benchmarking."""

    BASELINE = "baseline"
    CUSTOM = "custom"  # custom.md (our interpretation)
    PAPER_FAITHFUL = "paper_faithful"  # Appendix D condition 7


def _get_ollama_url() -> str:
    url = os.environ.get("OLLAMA_BASE_URL", OLLAMA_BASE_URL)
    parsed = urlparse(url)
    if parsed.hostname not in LOCALHOST_HOSTS:
        raise ValueError(f"OLLAMA_BASE_URL must point to localhost, got: {parsed.hostname}")
    return url


def _get_model(backend: str = "ollama") -> str:
    if backend == "openai":
        return os.environ.get("OPENAI_MODEL", OPENAI_MODEL)
    return os.environ.get("OLLAMA_MODEL", OLLAMA_MODEL)


def _load_contemplative_prompt() -> str:
    if CONTEMPLATIVE_PROMPT_PATH.exists():
        return CONTEMPLATIVE_PROMPT_PATH.read_text(encoding="utf-8")
    logger.warning("Contemplative prompt not found at %s, using empty", CONTEMPLATIVE_PROMPT_PATH)
    return ""


def _load_paper_faithful_template() -> str:
    if PAPER_FAITHFUL_PROMPT_PATH.exists():
        return PAPER_FAITHFUL_PROMPT_PATH.read_text(encoding="utf-8")
    logger.warning("Paper-faithful prompt not found at %s, using empty", PAPER_FAITHFUL_PROMPT_PATH)
    return ""


def _format_history(history: list[tuple[Move, Move]]) -> str:
    if not history:
        return "No previous rounds."
    lines = []
    for i, (my_move, opp_move) in enumerate(history, 1):
        lines.append(f"Round {i}: You={my_move.value}, Opponent={opp_move.value}")
    return "\n".join(lines)


def _strip_thinking(text: str) -> str:
    """Remove <think>...</think> blocks from model output."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def _parse_move(text: str) -> Move:
    """Parse LLM output to a Move, defaulting to COOPERATE on ambiguity."""
    cleaned = _strip_thinking(text).strip().upper()
    # Check for explicit keywords
    if re.search(r"\bDEFECT\b", cleaned):
        return Move.DEFECT
    if re.search(r"\bCOOPERATE\b", cleaned):
        return Move.COOPERATE
    # Fallback: any 'D' at start or 'C' at start
    if cleaned.startswith("D"):
        return Move.DEFECT
    return Move.COOPERATE


def _query_ollama(system: str, prompt: str, num_predict: int = 20) -> Optional[str]:
    """Send a prompt to Ollama and return the response text."""
    url = f"{_get_ollama_url()}/api/generate"
    payload = {
        "model": _get_model("ollama"),
        "prompt": prompt,
        "system": system,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": num_predict,
        },
    }
    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except (requests.RequestException, json.JSONDecodeError, KeyError) as exc:
        logger.error("Ollama request failed: %s", exc)
        return None


def _get_openai_key() -> str:
    """Get OpenAI API key from environment variable."""
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    return key


def _query_openai(system: str, prompt: str, max_tokens: int = 20) -> Optional[str]:
    """Send a prompt to OpenAI API and return the response text."""
    headers = {
        "Authorization": f"Bearer {_get_openai_key()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _get_model("openai"),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }
    try:
        response = requests.post(
            OPENAI_API_URL, headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.RequestException as exc:
        # Sanitize: do not log headers (contains API key)
        logger.error("OpenAI request failed: %s", type(exc).__name__)
        return None
    except (json.JSONDecodeError, KeyError, IndexError) as exc:
        logger.error("Failed to parse OpenAI response: %s", exc)
        return None


class LLMPlayer:
    """LLM-based IPD player.

    Args:
        contemplative: Deprecated. Use ``variant=PromptVariant.CUSTOM`` instead.
        label: Optional custom name for this player.
        backend: "ollama" (default) or "openai".
        variant: PromptVariant to use. Overrides ``contemplative`` if given.
    """

    def __init__(
        self,
        contemplative: bool = False,
        label: Optional[str] = None,
        backend: str = "ollama",
        variant: Optional[PromptVariant] = None,
    ) -> None:
        if variant is not None:
            self._variant = variant
        elif contemplative:
            warnings.warn(
                "contemplative=True is deprecated, use variant=PromptVariant.CUSTOM",
                DeprecationWarning,
                stacklevel=2,
            )
            self._variant = PromptVariant.CUSTOM
        else:
            self._variant = PromptVariant.BASELINE
        self._label = label
        self._backend = backend
        self._system_prompt = self._build_system_prompt()
        self._paper_template = ""
        if self._variant == PromptVariant.PAPER_FAITHFUL:
            self._paper_template = _load_paper_faithful_template()

    def _build_system_prompt(self) -> str:
        if self._variant == PromptVariant.CUSTOM:
            contemplative_text = _load_contemplative_prompt()
            return contemplative_text + "\n\n---\n\n" + GAME_SYSTEM_PROMPT
        if self._variant == PromptVariant.PAPER_FAITHFUL:
            # For paper_faithful, system prompt is minimal format instruction.
            # The contemplative template wraps the user_prompt in the prompt field.
            return (
                "You are playing the Iterated Prisoner's Dilemma. "
                "After your reflection, state your final decision as "
                "COOPERATE or DEFECT."
            )
        return GAME_SYSTEM_PROMPT

    @property
    def name(self) -> str:
        if self._label:
            return self._label
        model = _get_model(self._backend)
        suffix = f"+{self._variant.value}"
        return f"LLM({model}{suffix})"

    def choose(self, history: list[tuple[Move, Move]]) -> Move:
        history_text = _format_history(history)

        if self._variant == PromptVariant.PAPER_FAITHFUL:
            # Build user_prompt per Appendix D condition 7:
            # {user_prompt} = game context + history + "Your move this round:"
            user_prompt = (
                GAME_SYSTEM_PROMPT
                + "\n\nHistory:\n"
                + history_text
                + "\n\nYour move this round:"
            )
            # Insert into the paper template
            prompt = self._paper_template.replace("{user_prompt}", user_prompt)
            num_predict = 500
        else:
            prompt = f"History:\n{history_text}\n\nYour move this round:"
            num_predict = 20

        if self._backend == "openai":
            max_tokens = 500 if self._variant == PromptVariant.PAPER_FAITHFUL else 20
            result = _query_openai(self._system_prompt, prompt, max_tokens=max_tokens)
        else:
            result = _query_ollama(self._system_prompt, prompt, num_predict=num_predict)

        if result is None:
            logger.warning("LLM failed to respond, defaulting to COOPERATE")
            return Move.COOPERATE

        move = _parse_move(result)
        logger.debug("LLM response: %r -> %s", result.strip(), move.value)
        return move

    def reset(self) -> None:
        pass
