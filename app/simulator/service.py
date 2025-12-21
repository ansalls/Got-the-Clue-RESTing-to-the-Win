from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Iterable, List, Optional

from .. import models
from .engine import (
    BaseEventHook,
    BaseStrategy,
    SimulationEngine,
    SimulationMetrics,
    SimulationPlayer,
    get_registered_strategies,
)
from .hooks import TimelineHook
from .strategies import AggressiveStrategy, ConservativeStrategy, RandomStrategy


@dataclass(frozen=True)
class SimulationAssignment:
    player_id: int
    name: str
    strategy_key: str
    is_user: bool


@dataclass(frozen=True)
class SimulationOutcome:
    iterations: int
    rounds: int
    user_player_id: int
    user_strategy: str
    opponent_strategy: str
    assignments: List[SimulationAssignment]
    metrics: SimulationMetrics
    timeline: Optional[List[Dict[str, object]]]


def default_strategies() -> Dict[str, BaseStrategy]:
    return {
        "random": RandomStrategy(),
        "conservative": ConservativeStrategy(),
        "aggressive": AggressiveStrategy(),
    }


def _build_registry() -> Dict[str, BaseStrategy]:
    registry = default_strategies()
    registry.update(get_registered_strategies())
    return registry


def _build_assignments(
    players: Iterable[models.Player],
    user_player_id: int,
    user_strategy: str,
    opponent_strategy: str,
    overrides: Dict[int, str],
) -> List[SimulationAssignment]:
    assignments: List[SimulationAssignment] = []
    for player in players:
        is_user = player.id == user_player_id
        strategy_key = overrides.get(
            player.id,
            user_strategy if is_user else opponent_strategy,
        )
        assignments.append(
            SimulationAssignment(
                player_id=player.id,
                name=player.name,
                strategy_key=strategy_key,
                is_user=is_user,
            )
        )
    return assignments


def run_simulation(
    players: Iterable[models.Player],
    user_player_id: int,
    user_strategy: str,
    opponent_strategy: str,
    overrides: Dict[int, str],
    iterations: int,
    rounds: int,
    include_timeline: bool = False,
) -> SimulationOutcome:
    assignments = _build_assignments(
        players=players,
        user_player_id=user_player_id,
        user_strategy=user_strategy,
        opponent_strategy=opponent_strategy,
        overrides=overrides,
    )
    registry = _build_registry()
    metrics = SimulationMetrics()
    timeline_events: Optional[List[Dict[str, object]]] = [] if include_timeline else None
    hooks: Optional[List[BaseEventHook]] = None
    if include_timeline:
        hooks = [TimelineHook(events=timeline_events or [])]

    for _ in range(iterations):
        simulation_players = [
            SimulationPlayer(
                name=f"{assignment.name}#{assignment.player_id}",
                strategy_key=assignment.strategy_key,
                is_user=assignment.is_user,
            )
            for assignment in assignments
        ]
        engine = SimulationEngine(
            players=simulation_players,
            rounds=rounds,
            strategy_registry=registry,
            hooks=hooks,
        )
        result = engine.run()
        metrics.record_result(result)

    return SimulationOutcome(
        iterations=iterations,
        rounds=rounds,
        user_player_id=user_player_id,
        user_strategy=user_strategy,
        opponent_strategy=opponent_strategy,
        assignments=assignments,
        metrics=metrics,
        timeline=timeline_events,
    )


def serialize_assignments(assignments: Iterable[SimulationAssignment]) -> List[Dict[str, object]]:
    return [asdict(assignment) for assignment in assignments]
