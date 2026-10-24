"""Tests for the benchmark runner."""

from unittest.mock import patch

import pytest

from ipd.benchmark import (
    BenchmarkResult,
    MatchSummary,
    cohens_d,
    format_report,
    run_benchmark,
    save_results,
)
from ipd.game import Move
from ipd.strategies import AlwaysCooperate, TitForTat


class TestCohensD:
    def test_no_difference(self):
        assert cohens_d(0.5, 0.5, 100) == 0.0

    def test_positive_difference(self):
        d = cohens_d(0.3, 0.7, 100)
        assert d > 0

    def test_zero_n(self):
        assert cohens_d(0.5, 0.8, 0) == 0.0

    def test_zero_sd(self):
        # Both rates 0 or both 1 -> sd = 0
        assert cohens_d(0.0, 0.0, 100) == 0.0
        assert cohens_d(1.0, 1.0, 100) == 0.0


class TestBenchmarkResult:
    def test_empty(self):
        r = BenchmarkResult(model="test", mode="baseline")
        assert r.avg_cooperation_rate == 0.0
        assert r.avg_mutual_cooperation_rate == 0.0
        assert r.total_score == 0

    def test_with_matches(self):
        r = BenchmarkResult(model="test", mode="baseline", matches=[
            MatchSummary("opp1", 0.8, 50, 40, 0.6, 20),
            MatchSummary("opp2", 0.4, 30, 60, 0.2, 20),
        ])
        assert r.avg_cooperation_rate == pytest.approx(0.6)
        assert r.avg_mutual_cooperation_rate == pytest.approx(0.4)
        assert r.total_score == 80


class TestFormatReport:
    def test_produces_output(self):
        results = {
            "baseline": BenchmarkResult(
                model="test-baseline", mode="baseline",
                matches=[MatchSummary("TFT", 0.5, 40, 40, 0.5, 20)],
                elapsed_seconds=1.0,
            ),
            "custom": BenchmarkResult(
                model="test-custom", mode="custom",
                matches=[MatchSummary("TFT", 0.9, 55, 55, 0.8, 20)],
                elapsed_seconds=1.0,
            ),
        }
        report = format_report(results)
        assert "BASELINE" in report
        assert "CUSTOM" in report
        assert "Cohen's d" in report
        assert "COMPARISON" in report


class TestRunBenchmark:
    @patch("ipd.benchmark.LLMPlayer")
    def test_runs_against_opponents(self, mock_llm_cls):
        mock_player = mock_llm_cls.return_value
        mock_player.name = "MockLLM"
        mock_player.choose.return_value = Move.COOPERATE
        mock_player.reset.return_value = None

        opponents = [AlwaysCooperate(), TitForTat()]
        results = run_benchmark(num_rounds=5, opponents=opponents)

        assert "baseline" in results
        assert "custom" in results
        assert len(results["baseline"].matches) == 2
        assert len(results["custom"].matches) == 2


class TestSaveResults:
    def test_save_json(self, tmp_path):
        path = str(tmp_path / "results.json")
        results = {
            "baseline": BenchmarkResult(
                model="test", mode="baseline",
                matches=[MatchSummary("TFT", 0.5, 40, 40, 0.5, 20)],
            ),
            "custom": BenchmarkResult(
                model="test", mode="custom",
                matches=[MatchSummary("TFT", 0.9, 55, 55, 0.8, 20)],
            ),
        }
        save_results(results, path)

        import json
        with open(path) as f:
            data = json.load(f)
        assert "baseline" in data
        assert "custom" in data
        assert data["baseline"]["avg_cooperation_rate"] == 0.5


class TestPaperBenchmarkFailureCounts:
    """P3-03.1: failure counts land per simulation in the result JSON."""

    def test_counts_are_per_simulation_and_serialized(self, tmp_path):
        import json

        from ipd.benchmark import compute_paper_statistics, run_paper_benchmark, save_paper_results
        from ipd.llm_player import PromptVariant

        # 10 rounds per sim; the first reply of the run is unparseable, the
        # second is a failure, the rest are clean.
        replies = iter(["gibberish", None] + ["Choice: C"] * 1000)
        with patch("ipd.llm_player._query_ollama", side_effect=lambda *a, **k: next(replies)):
            res = run_paper_benchmark(
                num_simulations=2, num_rounds=10, variants=[PromptVariant.BASELINE]
            )
        first = res.simulations[0]
        assert (first.parse_fallback_count, first.llm_failure_count) == (1, 1)
        assert all(
            (s.parse_fallback_count, s.llm_failure_count) == (0, 0) for s in res.simulations[1:]
        )
        out = tmp_path / "r.json"
        try:
            stats = compute_paper_statistics(res)
        except Exception:  # scipy / statsmodels are optional extras
            stats = {}
        save_paper_results(res, stats, str(out))
        sims = json.loads(out.read_text())["simulations"]
        assert sims[0]["parse_fallback_count"] == 1 and sims[0]["llm_failure_count"] == 1
