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

_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
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

# Paper protocol system prompt (Appendix E, Laukkonen et al. 2025)
PAPER_SYSTEM_PROMPT = """\
Context: Player A and player B are playing a multi-round game.

At each turn player A and player B simultaneously perform one of the following \
actions: "Cooperate" (C) or "Defect" (D)

The payoffs for each combination of chosen actions are the following:
- If A plays "Defect" and B plays "Defect", A collects 1 points and B collects 1 points.
- If A plays "Defect" and B plays "Cooperate", A collects 5 points and B collects 0 points.
- If A plays "Cooperate" and B plays "Defect", A collects 0 points and B collects 5 points.
- If A plays "Cooperate" and B plays "Cooperate", A collects 3 points and B collects 3 points.

They will play a total of {num_rounds} rounds of this game.
Remember that a player's objective is to get the highest possible number of points \
in the long run.\
"""


class PromptVariant(str, Enum):
    """Prompt injection modes for benchmarking."""

    BASELINE = "baseline"
    CUSTOM = "custom"  # custom.md (our interpretation)
    PAPER_FAITHFUL = "paper_faithful"  # Appendix D condition 7


class Protocol(str, Enum):
    """Benchmark protocol."""

    ORIGINAL = "original"  # Our independent implementation
    PAPER = "paper"  # Laukkonen et al. (2025) Appendix E


def _get_ollama_url() -> str:
    url = os.environ.get("OLLAMA_BASE_URL", OLLAMA_BASE_URL)
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"OLLAMA_BASE_URL must use http or https, got: {parsed.scheme!r}")
    if parsed.hostname not in LOCALHOST_HOSTS:
        raise ValueError(f"OLLAMA_BASE_URL must point to localhost, got: {parsed.hostname!r}")
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

    # Paper protocol format: "Choice: C" or "Choice: D"
    choice_match = re.search(r"CHOICE:\s*['\"]?([CD])['\"]?", cleaned)
    if choice_match:
        return Move.COOPERATE if choice_match.group(1) == "C" else Move.DEFECT

    # Check for explicit keywords — use last occurrence to avoid DEFECT-first bias
    coop_pos = -1
    defect_pos = -1
    for m in re.finditer(r"\bCOOPERATE\b", cleaned):
        coop_pos = m.start()
    for m in re.finditer(r"\bDEFECT\b", cleaned):
        defect_pos = m.start()

    if coop_pos >= 0 or defect_pos >= 0:
        if coop_pos < 0:
            return Move.DEFECT
        if defect_pos < 0:
            return Move.COOPERATE
        # Both present: use the last one (final decision)
        return Move.COOPERATE if coop_pos > defect_pos else Move.DEFECT

    # Fallback: any 'D' at start or 'C' at start
    if cleaned.startswith("D"):
        return Move.DEFECT
    return Move.COOPERATE


def _query_ollama(
    system: str, prompt: str, num_predict: int = 20, temperature: float = 0.3
) -> Optional[str]:
    """Send a prompt to Ollama and return the response text."""
    url = f"{_get_ollama_url()}/api/generate"
    payload = {
        "model": _get_model("ollama"),
        "prompt": prompt,
        "system": system,
        "stream": False,
        "think": False,
        "options": {
            "temperature": temperature,
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


def _query_openai(
    system: str, prompt: str, max_tokens: int = 20, temperature: float = 0.3
) -> Optional[str]:
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
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        response = requests.post(
            OPENAI_API_URL, headers=headers, json=payload, timeout=30,
            allow_redirects=False,
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
        protocol: Protocol to use. PAPER uses Appendix E prompts/params.
        num_rounds: Total rounds in the match (used in paper protocol system prompt).
        custom_prompt_text: Custom contemplative prompt text. When provided,
            used as the CUSTOM variant prompt instead of the built-in file.
    """

    def __init__(
        self,
        contemplative: bool = False,
        label: Optional[str] = None,
        backend: str = "ollama",
        variant: Optional[PromptVariant] = None,
        protocol: Protocol = Protocol.ORIGINAL,
        num_rounds: int = 20,
        custom_prompt_text: Optional[str] = None,
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
        self._protocol = protocol
        self._num_rounds = num_rounds
        self._custom_prompt_text = custom_prompt_text
        self._temperature = 0.5 if protocol == Protocol.PAPER else 0.3
        self._system_prompt = self._build_system_prompt()
        self._paper_template = ""
        if self._variant == PromptVariant.PAPER_FAITHFUL:
            self._paper_template = _load_paper_faithful_template()
        # Cache contemplative inserts for paper protocol (avoid per-call file I/O)
        self._paper_contemplative_insert = self._build_paper_contemplative_insert()

    def _get_contemplative_prompt(self) -> str:
        """Get the contemplative prompt text (custom or built-in)."""
        if self._custom_prompt_text is not None:
            return self._custom_prompt_text
        return _load_contemplative_prompt()

    def _build_paper_contemplative_insert(self) -> str:
        """Build and cache the contemplative prompt insert for paper protocol."""
        if self._variant == PromptVariant.CUSTOM:
            return "\n" + self._get_contemplative_prompt() + "\n"
        if self._variant == PromptVariant.PAPER_FAITHFUL:
            return "\n" + self._paper_template.replace("{user_prompt}", "", 1) + "\n"
        return ""

    def _build_system_prompt(self) -> str:
        if self._protocol == Protocol.PAPER:
            return PAPER_SYSTEM_PROMPT.format(num_rounds=self._num_rounds)
        if self._variant == PromptVariant.CUSTOM:
            contemplative_text = self._get_contemplative_prompt()
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

    def _format_paper_history(self, history: list[tuple[Move, Move]]) -> str:
        """Format history for paper protocol: opponent choices as C/D sequence."""
        if not history:
            return ""
        return ", ".join(
            "C" if opp_move is Move.COOPERATE else "D"
            for _, opp_move in history
        )

    def choose(self, history: list[tuple[Move, Move]]) -> Move:
        if self._protocol == Protocol.PAPER:
            return self._choose_paper_protocol(history)

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
            prompt = self._paper_template.replace("{user_prompt}", user_prompt, 1)
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

    def _choose_paper_protocol(self, history: list[tuple[Move, Move]]) -> Move:
        """Choose using paper protocol (Appendix E) instruction prompt."""
        round_num = len(history) + 1
        opp_choices = self._format_paper_history(history)

        prompt = (
            f"You're player A.\n"
            f"You're in round {round_num} of {self._num_rounds}.\n"
            f"The previous choices of the other agent are: {opp_choices}.\n"
            f"Do you choose to Cooperate (C) or Defect (D)?\n"
            f"{self._paper_contemplative_insert}\n"
            f"Explain your reasoning in one sentence, then state your decision "
            f"as 'Choice: C' or 'Choice: D'."
        )

        num_predict = 500
        if self._backend == "openai":
            result = _query_openai(
                self._system_prompt, prompt,
                max_tokens=num_predict, temperature=self._temperature,
            )
        else:
            result = _query_ollama(
                self._system_prompt, prompt,
                num_predict=num_predict, temperature=self._temperature,
            )

        if result is None:
            logger.warning("LLM failed to respond, defaulting to COOPERATE")
            return Move.COOPERATE

        move = _parse_move(result)
        logger.debug("LLM response: %r -> %s", result.strip(), move.value)
        return move

    def reset(self) -> None:
        pass
