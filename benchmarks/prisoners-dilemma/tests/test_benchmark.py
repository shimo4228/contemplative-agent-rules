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
