from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import BaseStrategy, SimulationPlayer


@dataclass(frozen=True)
class RandomStrategy:
    key: str = "random"
    min_score: int = 1
    max_score: int = 6

    def choose_score(self, player: SimulationPlayer, round_number: int) -> int:
        return random.randint(self.min_score, self.max_score)


@dataclass(frozen=True)
class ConservativeStrategy:
    key: str = "conservative"
    fixed_score: int = 3

    def choose_score(self, player: SimulationPlayer, round_number: int) -> int:
        return self.fixed_score


@dataclass(frozen=True)
class AggressiveStrategy:
    key: str = "aggressive"
    base_score: int = 4

    def choose_score(self, player: SimulationPlayer, round_number: int) -> int:
        return self.base_score + (round_number % 2)
