"""Core Prisoner's Dilemma game engine."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import List, Protocol, Tuple


class Move(str, enum.Enum):
    COOPERATE = "cooperate"
    DEFECT = "defect"


# Standard payoff matrix (T > R > P > S, 2R > T + S)
# (row_payoff, col_payoff) for (row_move, col_move)
PAYOFF_MATRIX = {
    (Move.COOPERATE, Move.COOPERATE): (3, 3),  # R, R (mutual cooperation)
    (Move.COOPERATE, Move.DEFECT): (0, 5),     # S, T (sucker / temptation)
    (Move.DEFECT, Move.COOPERATE): (5, 0),     # T, S
    (Move.DEFECT, Move.DEFECT): (1, 1),        # P, P (mutual defection)
}


@dataclass(frozen=True)
class RoundResult:
    round_num: int
    move_a: Move
    move_b: Move
    payoff_a: int
    payoff_b: int


@dataclass
class MatchResult:
    player_a_name: str
    player_b_name: str
    rounds: List[RoundResult] = field(default_factory=list)

    @property
    def total_a(self) -> int:
        return sum(r.payoff_a for r in self.rounds)

    @property
    def total_b(self) -> int:
        return sum(r.payoff_b for r in self.rounds)

    @property
    def cooperation_rate_a(self) -> float:
        if not self.rounds:
            return 0.0
        return sum(1 for r in self.rounds if r.move_a is Move.COOPERATE) / len(self.rounds)

    @property
    def cooperation_rate_b(self) -> float:
        if not self.rounds:
            return 0.0
        return sum(1 for r in self.rounds if r.move_b is Move.COOPERATE) / len(self.rounds)

    @property
    def mutual_cooperation_rate(self) -> float:
        if not self.rounds:
            return 0.0
        return sum(
            1 for r in self.rounds
            if r.move_a is Move.COOPERATE and r.move_b is Move.COOPERATE
        ) / len(self.rounds)


class Player(Protocol):
    @property
    def name(self) -> str: ...

    def choose(self, history: List[Tuple[Move, Move]]) -> Move:
        """Choose a move given history of (my_move, opponent_move) pairs."""
        ...

    def reset(self) -> None:
        """Reset state for a new match."""
        ...


def play_round(
    player_a: Player,
    player_b: Player,
    history_a: List[Tuple[Move, Move]],
    history_b: List[Tuple[Move, Move]],
    round_num: int,
) -> RoundResult:
    """Play a single round."""
    move_a = player_a.choose(list(history_a))
    move_b = player_b.choose(list(history_b))
    payoff_a, payoff_b = PAYOFF_MATRIX[(move_a, move_b)]
    return RoundResult(
        round_num=round_num,
        move_a=move_a,
        move_b=move_b,
        payoff_a=payoff_a,
        payoff_b=payoff_b,
    )


def play_match(
    player_a: Player,
    player_b: Player,
    num_rounds: int = 20,
) -> MatchResult:
    """Play a full iterated match."""
    player_a.reset()
    player_b.reset()

    history_a: List[Tuple[Move, Move]] = []
    history_b: List[Tuple[Move, Move]] = []
    result = MatchResult(player_a_name=player_a.name, player_b_name=player_b.name)

    for i in range(num_rounds):
        round_result = play_round(player_a, player_b, history_a, history_b, i + 1)
        result.rounds.append(round_result)
        history_a.append((round_result.move_a, round_result.move_b))
        history_b.append((round_result.move_b, round_result.move_a))

    return result
