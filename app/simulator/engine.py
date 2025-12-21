from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, Iterable, List, Optional, Protocol


class SimulationEvent(str, Enum):
    INITIALIZED = "initialized"
    PLAYER_REGISTERED = "player_registered"
    GAME_STARTED = "game_started"
    GAME_COMPLETED = "game_completed"
    ROUND_STARTED = "round_started"
    ROUND_COMPLETED = "round_completed"


@dataclass(frozen=True)
class SimulationPlayer:
    name: str
    strategy_key: str
    is_user: bool = False


@dataclass(frozen=True)
class SimulationResult:
    winner: SimulationPlayer
    rounds_played: int


@dataclass(frozen=True)
class SimulationRound:
    number: int
    scores: Dict[str, int]
    round_winner: SimulationPlayer


class BaseStrategy(Protocol):
    key: str

    def choose_score(self, player: SimulationPlayer, round_number: int) -> int:
        ...


class BaseEventHook(Protocol):
    def handle(self, event: SimulationEvent, payload: Dict[str, object]) -> None:
        ...


_STRATEGIES: Dict[str, BaseStrategy] = {}
_HOOKS: List[BaseEventHook] = []


def register_strategy(strategy: BaseStrategy) -> None:
    _STRATEGIES[strategy.key] = strategy


def get_registered_strategies() -> Dict[str, BaseStrategy]:
    return dict(_STRATEGIES)


def register_hook(hook: BaseEventHook) -> None:
    _HOOKS.append(hook)


def _dispatch_event(event: SimulationEvent, payload: Dict[str, object]) -> None:
    for hook in _HOOKS:
        hook.handle(event, payload)


class SimulationEngine:
    def __init__(
        self,
        players: Iterable[SimulationPlayer],
        rounds: int = 5,
        strategy_registry: Optional[Dict[str, BaseStrategy]] = None,
        hooks: Optional[List[BaseEventHook]] = None,
    ) -> None:
        self.players = list(players)
        self.rounds = rounds
        self.strategy_registry = strategy_registry or _STRATEGIES
        self.hooks = hooks or _HOOKS
        self._notify = _dispatch_event if hooks is None else self._make_dispatcher()
        self._notify(SimulationEvent.INITIALIZED, {"players": self.players, "rounds": rounds})

    def _make_dispatcher(self) -> Callable[[SimulationEvent, Dict[str, object]], None]:
        def _dispatcher(event: SimulationEvent, payload: Dict[str, object]) -> None:
            for hook in self.hooks:
                hook.handle(event, payload)

        return _dispatcher

    def run(self) -> SimulationResult:
        for player in self.players:
            if player.strategy_key not in self.strategy_registry:
                raise ValueError(f"Strategy '{player.strategy_key}' is not registered")
            self._notify(SimulationEvent.PLAYER_REGISTERED, {"player": player})

        scores = {player.name: 0 for player in self.players}
        rounds_played: List[SimulationRound] = []

        self._notify(SimulationEvent.GAME_STARTED, {"players": self.players})
        for round_number in range(1, self.rounds + 1):
            self._notify(SimulationEvent.ROUND_STARTED, {"round": round_number})
            round_scores: Dict[str, int] = {}
            for player in self.players:
                strategy = self.strategy_registry[player.strategy_key]
                round_scores[player.name] = strategy.choose_score(player, round_number)
                scores[player.name] += round_scores[player.name]

            round_winner = max(self.players, key=lambda player: round_scores[player.name])
            round_summary = SimulationRound(
                number=round_number,
                scores=round_scores,
                round_winner=round_winner,
            )
            rounds_played.append(round_summary)
            self._notify(
                SimulationEvent.ROUND_COMPLETED,
                {"round": round_summary, "round_scores": round_scores},
            )

        winner = max(self.players, key=lambda player: scores[player.name])
        result = SimulationResult(winner=winner, rounds_played=self.rounds)
        self._notify(
            SimulationEvent.GAME_COMPLETED,
            {"result": result, "scores": scores, "rounds": rounds_played},
        )
        return result


@dataclass
class SimulationMetrics:
    user_wins: int = 0
    total_games: int = 0
    per_strategy_wins: Dict[str, int] = field(default_factory=dict)

    def record_result(self, result: SimulationResult) -> None:
        self.total_games += 1
        self.per_strategy_wins[result.winner.strategy_key] = (
            self.per_strategy_wins.get(result.winner.strategy_key, 0) + 1
        )
        if result.winner.is_user:
            self.user_wins += 1

    def win_percentage(self, strategy_key: Optional[str] = None) -> float:
        if self.total_games == 0:
            return 0.0
        if strategy_key is None:
            return self.user_wins / self.total_games * 100
        return self.per_strategy_wins.get(strategy_key, 0) / self.total_games * 100
