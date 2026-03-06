"""Benchmark runner: compare baseline vs contemplative LLM across opponents."""

from __future__ import annotations

import json
import logging
import math
import time
from dataclasses import asdict, dataclass, field
from typing import Dict, List

from .game import MatchResult, Player, play_match
from .llm_player import LLMPlayer
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
    mode: str  # "baseline" or "contemplative"
    matches: List[MatchSummary] = field(default_factory=list)
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


def _default_opponents() -> List[Player]:
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
    opponents: List[Player] | None = None,
    backend: str = "ollama",
) -> Dict[str, BenchmarkResult]:
    """Run baseline and contemplative LLM against all opponents.

    Returns dict with keys "baseline" and "contemplative".
    """
    if opponents is None:
        opponents = _default_opponents()

    results: Dict[str, BenchmarkResult] = {}

    for mode in ("baseline", "contemplative"):
        is_contemplative = mode == "contemplative"
        llm = LLMPlayer(contemplative=is_contemplative, backend=backend)

        bench = BenchmarkResult(model=llm.name, mode=mode)
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
        results[mode] = bench

    return results


def cohens_d(rate_baseline: float, rate_contemplative: float, n: int) -> float:
    """Compute Cohen's d for cooperation rate difference.

    Uses a simple approximation assuming binomial proportions.
    """
    if n == 0:
        return 0.0
    # Pooled standard deviation for proportions
    p_avg = (rate_baseline + rate_contemplative) / 2
    sd = math.sqrt(p_avg * (1 - p_avg))
    if sd == 0:
        return 0.0
    return (rate_contemplative - rate_baseline) / sd


def format_report(results: Dict[str, BenchmarkResult]) -> str:
    """Format benchmark results as a human-readable report."""
    lines = ["=" * 60, "Iterated Prisoner's Dilemma Benchmark Report", "=" * 60, ""]

    for mode in ("baseline", "contemplative"):
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

    # Comparison
    baseline = results["baseline"]
    contemplative = results["contemplative"]
    total_rounds = sum(m.num_rounds for m in baseline.matches)
    d = cohens_d(baseline.avg_cooperation_rate, contemplative.avg_cooperation_rate, total_rounds)

    lines.append("--- COMPARISON ---")
    lines.append(f"Baseline avg coop:       {baseline.avg_cooperation_rate*100:.1f}%")
    lines.append(f"Contemplative avg coop:  {contemplative.avg_cooperation_rate*100:.1f}%")
    lines.append(f"Cooperation delta:       {(contemplative.avg_cooperation_rate - baseline.avg_cooperation_rate)*100:+.1f}%")
    lines.append(f"Cohen's d:               {d:.2f}")
    lines.append(f"Paper reference:         d > 7")
    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


def save_results(results: Dict[str, BenchmarkResult], path: str) -> None:
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
