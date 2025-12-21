from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas
from ..database import get_db
from ..simulator import service as simulation_service


router = APIRouter(
    prefix="/games",
    tags=["Simulations"],
)


@router.post("/{game_id}/simulate", response_model=schemas.SimulationResponse)
def simulate_game(
    game_id: int,
    request: schemas.SimulationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    if game.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to simulate this game")

    players = (
        db.query(models.Player)
        .filter(models.Player.game_id == game_id)
        .order_by(models.Player.seat_order.asc())
        .all()
    )
    if not players:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Game has no players to simulate")

    if request.user_player_id not in {player.id for player in players}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User player not found in this game")

    overrides: Dict[int, str] = {override.player_id: override.strategy_key for override in request.strategy_overrides}

    outcome = simulation_service.run_simulation(
        players=players,
        user_player_id=request.user_player_id,
        user_strategy=request.user_strategy,
        opponent_strategy=request.opponent_strategy,
        overrides=overrides,
        iterations=request.iterations,
        rounds=request.rounds,
        include_timeline=request.include_timeline,
    )

    metrics = outcome.metrics

    return schemas.SimulationResponse(
        iterations=outcome.iterations,
        rounds=outcome.rounds,
        user_player_id=outcome.user_player_id,
        user_strategy=outcome.user_strategy,
        opponent_strategy=outcome.opponent_strategy,
        user_win_percentage=metrics.win_percentage(),
        strategy_win_percentages={
            strategy: metrics.win_percentage(strategy)
            for strategy in metrics.per_strategy_wins
        },
        strategy_win_counts=metrics.per_strategy_wins,
        assignments=[
            schemas.SimulationAssignmentOut(**assignment)
            for assignment in simulation_service.serialize_assignments(outcome.assignments)
        ],
        timeline=outcome.timeline,
    )
