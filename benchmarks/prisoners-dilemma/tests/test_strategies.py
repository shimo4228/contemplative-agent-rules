"""Tests for fixed strategy players."""

from ipd.game import Move
from ipd.strategies import (
    AlwaysCooperate,
    AlwaysDefect,
    GrimTrigger,
    RandomPlayer,
    SuspiciousTitForTat,
    TitForTat,
)


class TestAlwaysCooperate:
    def test_always_cooperates(self):
        p = AlwaysCooperate()
        assert p.choose([]) is Move.COOPERATE
        assert p.choose([(Move.COOPERATE, Move.DEFECT)]) is Move.COOPERATE

    def test_name(self):
        assert AlwaysCooperate().name == "AlwaysCooperate"


class TestAlwaysDefect:
    def test_always_defects(self):
        p = AlwaysDefect()
        assert p.choose([]) is Move.DEFECT
        assert p.choose([(Move.DEFECT, Move.COOPERATE)]) is Move.DEFECT


class TestTitForTat:
    def test_cooperates_first(self):
        assert TitForTat().choose([]) is Move.COOPERATE

    def test_copies_opponent(self):
        p = TitForTat()
        assert p.choose([(Move.COOPERATE, Move.DEFECT)]) is Move.DEFECT
        assert p.choose([(Move.COOPERATE, Move.COOPERATE)]) is Move.COOPERATE


class TestGrimTrigger:
    def test_cooperates_initially(self):
        p = GrimTrigger()
        assert p.choose([]) is Move.COOPERATE

    def test_triggers_on_defection(self):
        p = GrimTrigger()
        assert p.choose([(Move.COOPERATE, Move.DEFECT)]) is Move.DEFECT
        # Once triggered, stays defecting
        assert p.choose([(Move.COOPERATE, Move.DEFECT), (Move.DEFECT, Move.COOPERATE)]) is Move.DEFECT

    def test_reset(self):
        p = GrimTrigger()
        p.choose([(Move.COOPERATE, Move.DEFECT)])  # trigger
        p.reset()
        assert p.choose([]) is Move.COOPERATE


class TestRandomPlayer:
    def test_deterministic_with_seed(self):
        p1 = RandomPlayer(coop_prob=0.5, seed=42)
        p2 = RandomPlayer(coop_prob=0.5, seed=42)
        moves1 = [p1.choose([]) for _ in range(20)]
        moves2 = [p2.choose([]) for _ in range(20)]
        assert moves1 == moves2

    def test_reset_reproduces(self):
        p = RandomPlayer(coop_prob=0.5, seed=42)
        first_run = [p.choose([]) for _ in range(10)]
        p.reset()
        second_run = [p.choose([]) for _ in range(10)]
        assert first_run == second_run

    def test_always_cooperate(self):
        p = RandomPlayer(coop_prob=1.0, seed=0)
        for _ in range(20):
            assert p.choose([]) is Move.COOPERATE

    def test_always_defect(self):
        p = RandomPlayer(coop_prob=0.0, seed=0)
        for _ in range(20):
            assert p.choose([]) is Move.DEFECT


class TestSuspiciousTitForTat:
    def test_defects_first(self):
        assert SuspiciousTitForTat().choose([]) is Move.DEFECT

    def test_copies_opponent(self):
        p = SuspiciousTitForTat()
        assert p.choose([(Move.DEFECT, Move.COOPERATE)]) is Move.COOPERATE
        assert p.choose([(Move.COOPERATE, Move.DEFECT)]) is Move.DEFECT
