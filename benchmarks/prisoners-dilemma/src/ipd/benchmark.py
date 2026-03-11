"""Benchmark runner: compare baseline, custom, and paper_faithful LLM across opponents."""

from __future__ import annotations

import json
import logging
import math
import time
from dataclasses import asdict, dataclass, field
from typing import Optional, Sequence

from .game import MatchResult, Player, play_match
from .llm_player import LLMPlayer, PromptVariant
from .strategies import (
    AlwaysCooperate,
    AlwaysDefect,
    GrimTrigger,
    RandomPlayer,
    SuspiciousTitForTat,
    TitForTat,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MatchSummary:
    opponent: str
    cooperation_rate: float
    total_score: int
    opponent_score: int
    mutual_cooperation_rate: float
    num_rounds: int


@dataclass
class BenchmarkResult:
    model: str
    mode: str  # "baseline", "custom", or "paper_faithful"
    matches: list[MatchSummary] = field(default_factory=list)
    elapsed_seconds: float = 0.0

    @property
    def avg_cooperation_rate(self) -> float:
        if not self.matches:
            return 0.0
        return sum(m.cooperation_rate for m in self.matches) / len(self.matches)

    @property
    def avg_mutual_cooperation_rate(self) -> float:
        if not self.matches:
            return 0.0
        return sum(m.mutual_cooperation_rate for m in self.matches) / len(self.matches)

    @property
    def total_score(self) -> int:
        return sum(m.total_score for m in self.matches)


def _default_opponents() -> list[Player]:
    return [
        TitForTat(),
        AlwaysCooperate(),
        AlwaysDefect(),
        GrimTrigger(),
        SuspiciousTitForTat(),
        RandomPlayer(coop_prob=0.5, seed=42),
    ]


def _summarize_match(result: MatchResult) -> MatchSummary:
    return MatchSummary(
        opponent=result.player_b_name,
        cooperation_rate=result.cooperation_rate_a,
        total_score=result.total_a,
        opponent_score=result.total_b,
        mutual_cooperation_rate=result.mutual_cooperation_rate,
        num_rounds=len(result.rounds),
    )


def run_benchmark(
    num_rounds: int = 20,
    opponents: list[Player] | None = None,
    backend: str = "ollama",
    variants: Optional[Sequence[PromptVariant]] = None,
) -> dict[str, BenchmarkResult]:
    """Run LLM against all opponents for each variant.

    Args:
        num_rounds: Rounds per match.
        opponents: List of opponent strategies. Defaults to 6 standard opponents.
        backend: "ollama" or "openai".
        variants: Which prompt variants to run. Defaults to baseline + custom.

    Returns:
        Dict keyed by variant value (e.g. "baseline", "custom", "paper_faithful").
    """
    if opponents is None:
        opponents = _default_opponents()
    if variants is None:
        variants = [PromptVariant.BASELINE, PromptVariant.CUSTOM]

    results: dict[str, BenchmarkResult] = {}

    for variant in variants:
        llm = LLMPlayer(variant=variant, backend=backend)

        bench = BenchmarkResult(model=llm.name, mode=variant.value)
        start = time.time()

        for opponent in opponents:
            logger.info("Playing %s vs %s (%d rounds)", llm.name, opponent.name, num_rounds)
            match_result = play_match(llm, opponent, num_rounds=num_rounds)
            summary = _summarize_match(match_result)
            bench.matches.append(summary)
            logger.info(
                "  %s: coop=%.0f%%, score=%d vs %d",
                opponent.name,
                summary.cooperation_rate * 100,
                summary.total_score,
                summary.opponent_score,
            )

        bench.elapsed_seconds = time.time() - start
        results[variant.value] = bench

    return results


def cohens_d(rate_a: float, rate_b: float, n: int) -> float:
    """Compute Cohen's d for cooperation rate difference.

    Uses a simple approximation assuming binomial proportions.
    """
    if n == 0:
        return 0.0
    # Pooled standard deviation for proportions
    p_avg = (rate_a + rate_b) / 2
    sd = math.sqrt(p_avg * (1 - p_avg))
    if sd == 0:
        return 0.0
    return (rate_b - rate_a) / sd


def format_report(results: dict[str, BenchmarkResult]) -> str:
    """Format benchmark results as a human-readable report."""
    lines = ["=" * 70, "Iterated Prisoner's Dilemma Benchmark Report", "=" * 70, ""]

    variant_order = [v for v in ("baseline", "custom", "paper_faithful") if v in results]

    for mode in variant_order:
        bench = results[mode]
        lines.append(f"--- {mode.upper()} ({bench.model}) ---")
        lines.append(f"Time: {bench.elapsed_seconds:.1f}s")
        lines.append("")
        lines.append(f"{'Opponent':<22} {'Coop%':>6} {'MCoop%':>7} {'Score':>6} {'Opp':>6}")
        lines.append("-" * 50)
        for m in bench.matches:
            lines.append(
                f"{m.opponent:<22} {m.cooperation_rate*100:>5.0f}% "
                f"{m.mutual_cooperation_rate*100:>5.0f}%  "
                f"{m.total_score:>5} {m.opponent_score:>5}"
            )
        lines.append("")
        lines.append(f"Avg cooperation: {bench.avg_cooperation_rate*100:.1f}%")
        lines.append(f"Avg mutual coop: {bench.avg_mutual_cooperation_rate*100:.1f}%")
        lines.append(f"Total score: {bench.total_score}")
        lines.append("")

    # Pairwise comparisons against baseline
    if "baseline" in results:
        baseline = results["baseline"]
        total_rounds = sum(m.num_rounds for m in baseline.matches)
        lines.append("--- COMPARISON (vs baseline) ---")
        lines.append(f"Baseline avg coop:       {baseline.avg_cooperation_rate*100:.1f}%")
        lines.append("")

        for mode in variant_order:
            if mode == "baseline":
                continue
            bench = results[mode]
            d = cohens_d(
                baseline.avg_cooperation_rate,
                bench.avg_cooperation_rate,
                total_rounds,
            )
            delta = bench.avg_cooperation_rate - baseline.avg_cooperation_rate
            lines.append(f"  {mode}:")
            lines.append(f"    Avg coop:            {bench.avg_cooperation_rate*100:.1f}%")
            lines.append(f"    Cooperation delta:   {delta*100:+.1f}%")
            lines.append(f"    Cohen's d:           {d:.2f}")
            lines.append("")

        lines.append(f"Paper reference:         d > 7 (Contemplative vs Standard, Mixed opponent)")
        lines.append("")

    lines.append("=" * 70)

    return "\n".join(lines)


def save_results(results: dict[str, BenchmarkResult], path: str) -> None:
    """Save results to JSON."""
    data = {}
    for mode, bench in results.items():
        data[mode] = {
            "model": bench.model,
            "mode": bench.mode,
            "elapsed_seconds": bench.elapsed_seconds,
            "avg_cooperation_rate": bench.avg_cooperation_rate,
            "avg_mutual_cooperation_rate": bench.avg_mutual_cooperation_rate,
            "total_score": bench.total_score,
            "matches": [asdict(m) for m in bench.matches],
        }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
