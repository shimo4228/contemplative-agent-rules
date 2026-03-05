"""Fixed strategy players for the Iterated Prisoner's Dilemma."""

from __future__ import annotations

import random
from typing import List, Tuple

from .game import Move


class AlwaysCooperate:
    """Always cooperates."""

    @property
    def name(self) -> str:
        return "AlwaysCooperate"

    def choose(self, history: List[Tuple[Move, Move]]) -> Move:
        return Move.COOPERATE

    def reset(self) -> None:
        pass


class AlwaysDefect:
    """Always defects."""

    @property
    def name(self) -> str:
        return "AlwaysDefect"

    def choose(self, history: List[Tuple[Move, Move]]) -> Move:
        return Move.DEFECT

    def reset(self) -> None:
        pass


class TitForTat:
    """Cooperates first, then copies opponent's last move."""

    @property
    def name(self) -> str:
        return "TitForTat"

    def choose(self, history: List[Tuple[Move, Move]]) -> Move:
        if not history:
            return Move.COOPERATE
        return history[-1][1]  # opponent's last move

    def reset(self) -> None:
        pass


class GrimTrigger:
    """Cooperates until opponent defects, then defects forever."""

    def __init__(self) -> None:
        self._triggered = False

    @property
    def name(self) -> str:
        return "GrimTrigger"

    def choose(self, history: List[Tuple[Move, Move]]) -> Move:
        if self._triggered:
            return Move.DEFECT
        if history and history[-1][1] is Move.DEFECT:
            self._triggered = True
            return Move.DEFECT
        return Move.COOPERATE

    def reset(self) -> None:
        self._triggered = False


class RandomPlayer:
    """Cooperates with a given probability."""

    def __init__(self, coop_prob: float = 0.5, seed: int | None = None) -> None:
        self._coop_prob = coop_prob
        self._seed = seed
        self._rng = random.Random(seed)

    @property
    def name(self) -> str:
        return f"Random(p={self._coop_prob})"

    def choose(self, history: List[Tuple[Move, Move]]) -> Move:
        if self._rng.random() < self._coop_prob:
            return Move.COOPERATE
        return Move.DEFECT

    def reset(self) -> None:
        self._rng = random.Random(self._seed)


class SuspiciousTitForTat:
    """Defects first, then copies opponent's last move."""

    @property
    def name(self) -> str:
        return "SuspiciousTitForTat"

    def choose(self, history: List[Tuple[Move, Move]]) -> Move:
        if not history:
            return Move.DEFECT
        return history[-1][1]

    def reset(self) -> None:
        pass
