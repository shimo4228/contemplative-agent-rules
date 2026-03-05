"""Tests for the core game engine."""

from ipd.game import MatchResult, Move, PAYOFF_MATRIX, RoundResult, play_match, play_round
from ipd.strategies import AlwaysCooperate, AlwaysDefect, TitForTat


class TestMove:
    def test_values(self):
        assert Move.COOPERATE == "cooperate"
        assert Move.DEFECT == "defect"


class TestPayoffMatrix:
    def test_mutual_cooperation(self):
        assert PAYOFF_MATRIX[(Move.COOPERATE, Move.COOPERATE)] == (3, 3)

    def test_mutual_defection(self):
        assert PAYOFF_MATRIX[(Move.DEFECT, Move.DEFECT)] == (1, 1)

    def test_temptation(self):
        assert PAYOFF_MATRIX[(Move.DEFECT, Move.COOPERATE)] == (5, 0)

    def test_sucker(self):
        assert PAYOFF_MATRIX[(Move.COOPERATE, Move.DEFECT)] == (0, 5)

    def test_constraints(self):
        # T > R > P > S
        t, r, p, s = 5, 3, 1, 0
        assert t > r > p > s
        # 2R > T + S (cooperation is better than alternating)
        assert 2 * r > t + s


class TestPlayRound:
    def test_both_cooperate(self):
        a, b = AlwaysCooperate(), AlwaysCooperate()
        result = play_round(a, b, [], [], 1)
        assert result.move_a is Move.COOPERATE
        assert result.move_b is Move.COOPERATE
        assert result.payoff_a == 3
        assert result.payoff_b == 3

    def test_defect_vs_cooperate(self):
        a, b = AlwaysDefect(), AlwaysCooperate()
        result = play_round(a, b, [], [], 1)
        assert result.move_a is Move.DEFECT
        assert result.move_b is Move.COOPERATE
        assert result.payoff_a == 5
        assert result.payoff_b == 0


class TestPlayMatch:
    def test_cooperators(self):
        result = play_match(AlwaysCooperate(), AlwaysCooperate(), num_rounds=10)
        assert len(result.rounds) == 10
        assert result.total_a == 30
        assert result.total_b == 30
        assert result.cooperation_rate_a == 1.0
        assert result.cooperation_rate_b == 1.0
        assert result.mutual_cooperation_rate == 1.0

    def test_defectors(self):
        result = play_match(AlwaysDefect(), AlwaysDefect(), num_rounds=10)
        assert result.total_a == 10
        assert result.total_b == 10
        assert result.cooperation_rate_a == 0.0
        assert result.mutual_cooperation_rate == 0.0

    def test_tft_vs_cooperator(self):
        result = play_match(TitForTat(), AlwaysCooperate(), num_rounds=10)
        assert result.cooperation_rate_a == 1.0  # TFT mirrors cooperator
        assert result.total_a == 30

    def test_tft_vs_defector(self):
        result = play_match(TitForTat(), AlwaysDefect(), num_rounds=10)
        # TFT cooperates round 1, then defects
        assert result.rounds[0].move_a is Move.COOPERATE
        for r in result.rounds[1:]:
            assert r.move_a is Move.DEFECT


class TestMatchResult:
    def test_empty(self):
        r = MatchResult(player_a_name="a", player_b_name="b")
        assert r.total_a == 0
        assert r.cooperation_rate_a == 0.0
        assert r.mutual_cooperation_rate == 0.0
