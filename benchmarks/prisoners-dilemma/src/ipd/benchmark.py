"""Benchmark runner: compare baseline, custom, and paper_faithful LLM across opponents."""

from __future__ import annotations

import json
import logging
import math
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Optional, Sequence

from .game import MatchResult, Player, play_match
from .llm_player import LLMPlayer, PromptVariant, Protocol
from .strategies import (
    AlwaysCooperate,
    AlwaysDefect,
    GrimTrigger,
    ProbabilisticOpponent,
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


# --- Paper protocol (Appendix E) ---


@dataclass(frozen=True)
class SimulationResult:
    """Result of a single simulation (one game of N rounds)."""

    variant: str
    opponent_alpha: float
    cooperation_rate: float
    total_score: int
    opponent_score: int


@dataclass
class PaperBenchmarkResult:
    """Aggregated results across multiple simulations for paper protocol."""

    model: str
    num_simulations: int
    num_rounds: int
    simulations: list[SimulationResult] = field(default_factory=list)
    elapsed_seconds: float = 0.0

    def cooperation_rates_by(
        self, variant: str, alpha: float
    ) -> list[float]:
        """Get cooperation rates for a specific variant and opponent."""
        return [
            s.cooperation_rate
            for s in self.simulations
            if s.variant == variant and s.opponent_alpha == alpha
        ]


def run_paper_benchmark(
    num_simulations: int = 50,
    num_rounds: int = 10,
    backend: str = "ollama",
    variants: Optional[Sequence[PromptVariant]] = None,
) -> PaperBenchmarkResult:
    """Run benchmark using paper protocol (Appendix E).

    Args:
        num_simulations: Number of independent simulations per condition.
        num_rounds: Rounds per game (paper uses 10).
        backend: "ollama" or "openai".
        variants: Prompt variants to test.

    Returns:
        PaperBenchmarkResult with all simulation data.
    """
    if variants is None:
        variants = [PromptVariant.BASELINE, PromptVariant.CUSTOM]

    alphas = [0.0, 0.5, 1.0]
    simulations: list[SimulationResult] = []
    model_name = ""
    start = time.time()

    for variant in variants:
        llm = LLMPlayer(
            variant=variant,
            backend=backend,
            protocol=Protocol.PAPER,
            num_rounds=num_rounds,
        )
        if not model_name:
            model_name = llm.name

        for alpha in alphas:
            for sim in range(num_simulations):
                seed = 42 + sim
                opponent = ProbabilisticOpponent(alpha=alpha, seed=seed)

                logger.info(
                    "Sim %d/%d: %s vs α=%.1f (%s)",
                    sim + 1, num_simulations, variant.value, alpha, llm.name,
                )
                match = play_match(llm, opponent, num_rounds=num_rounds)
                simulations.append(SimulationResult(
                    variant=variant.value,
                    opponent_alpha=alpha,
                    cooperation_rate=match.cooperation_rate_a,
                    total_score=match.total_a + match.total_b,
                    opponent_score=match.total_b,
                ))

    elapsed = time.time() - start
    return PaperBenchmarkResult(
        model=model_name,
        num_simulations=num_simulations,
        num_rounds=num_rounds,
        simulations=simulations,
        elapsed_seconds=elapsed,
    )


def _cohens_d_from_arrays(
    rates: Any, baseline_rates: Any, variant: str
) -> tuple[float, float]:
    """Compute mean difference and Cohen's d vs baseline.

    Returns (mean_diff, cohens_d). Returns (0.0, 0.0) for baseline itself
    or when baseline is empty.
    """
    import numpy as np

    if len(baseline_rates) == 0 or variant == "baseline":
        return 0.0, 0.0

    mean_diff = float(rates.mean() - baseline_rates.mean())
    rate_sd = float(rates.std(ddof=1))
    base_sd = float(baseline_rates.std(ddof=1))

    if rate_sd == 0 and base_sd == 0:
        return mean_diff, 0.0

    pooled_sd = float(np.sqrt((rate_sd ** 2 + base_sd ** 2) / 2))
    d = mean_diff / pooled_sd if pooled_sd > 0 else 0.0
    return mean_diff, d


def compute_paper_statistics(
    result: PaperBenchmarkResult,
) -> dict:
    """Compute ANOVA + Tukey HSD + Cohen's d for paper benchmark results.

    Returns dict with per-opponent-alpha statistics.
    """
    try:
        import numpy as np
        from scipy import stats as sp_stats
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
    except ImportError:
        raise RuntimeError(
            "scipy, statsmodels, and numpy are required for paper protocol statistics. "
            "Install with: pip install -e '.[paper]'"
        )

    variants = sorted({s.variant for s in result.simulations})
    alphas = sorted({s.opponent_alpha for s in result.simulations})

    output: dict = {}
    for alpha in alphas:
        alpha_key = f"alpha_{alpha}"
        groups = {}
        for v in variants:
            rates = result.cooperation_rates_by(v, alpha)
            groups[v] = rates

        # ANOVA
        group_arrays = [np.array(groups[v]) for v in variants]
        if len(group_arrays) >= 2:
            f_stat, p_value = sp_stats.f_oneway(*group_arrays)
        else:
            f_stat, p_value = 0.0, 1.0

        # Tukey HSD
        all_rates = []
        all_labels = []
        for v in variants:
            all_rates.extend(groups[v])
            all_labels.extend([v] * len(groups[v]))

        tukey = pairwise_tukeyhsd(np.array(all_rates), np.array(all_labels))

        # Per-variant stats
        baseline_rates = np.array(groups.get("baseline", []))
        variant_stats = {}
        for v in variants:
            rates = np.array(groups[v])
            mean_diff, d = _cohens_d_from_arrays(rates, baseline_rates, v)

            variant_stats[v] = {
                "mean_rate": float(rates.mean()),
                "std_dev": float(rates.std(ddof=1)) if len(rates) > 1 else 0.0,
                "sample_size": len(rates),
                "mean_diff_from_baseline": mean_diff,
                "cohens_d": d,
            }

        output[alpha_key] = {
            "anova_f_statistic": float(f_stat),
            "anova_p_value": float(p_value),
            "tukey_summary": str(tukey),
            "variants": variant_stats,
        }

    return output


def save_paper_results(result: PaperBenchmarkResult, stats: dict, path: str) -> None:
    """Save paper protocol results and statistics to JSON."""
    data = {
        "protocol": "paper",
        "model": result.model,
        "num_simulations": result.num_simulations,
        "num_rounds": result.num_rounds,
        "elapsed_seconds": result.elapsed_seconds,
        "statistics": stats,
        "simulations": [asdict(s) for s in result.simulations],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def format_paper_report(result: PaperBenchmarkResult, stats: dict) -> str:
    """Format paper protocol results as a human-readable report."""
    lines = [
        "=" * 70,
        "IPD Benchmark Report — Paper Protocol (Appendix E)",
        "=" * 70,
        f"Model: {result.model}",
        f"Simulations: {result.num_simulations} per condition",
        f"Rounds: {result.num_rounds}",
        f"Time: {result.elapsed_seconds:.1f}s",
        "",
    ]

    for alpha_key, alpha_stats in stats.items():
        alpha = alpha_key.replace("alpha_", "α=")
        lines.append(f"--- Opponent {alpha} ---")
        lines.append(
            f"ANOVA: F={alpha_stats['anova_f_statistic']:.4f}, "
            f"p={alpha_stats['anova_p_value']:.6f}"
        )
        lines.append("")
        lines.append(
            f"{'Variant':<20} {'Mean':>6} {'SD':>6} {'n':>4} "
            f"{'Diff':>7} {'d':>6}"
        )
        lines.append("-" * 55)
        for v, vs in alpha_stats["variants"].items():
            lines.append(
                f"{v:<20} {vs['mean_rate']*100:>5.1f}% "
                f"{vs['std_dev']*100:>5.1f}% {vs['sample_size']:>4} "
                f"{vs['mean_diff_from_baseline']*100:>+6.1f}% "
                f"{vs['cohens_d']:>5.2f}"
            )
        lines.append("")

    lines.append("=" * 70)
    return "\n".join(lines)
