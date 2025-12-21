from typing import Optional

from fastapi import HTTPException, status

from .. import models


def require_game_exists(game: Optional[models.Game]) -> models.Game:
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return game


def require_game_owner(game: models.Game, current_user: models.User) -> None:
    if game.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this game")


def require_setup_state(game: models.Game) -> None:
    if game.status != "setup":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Game setup is already finalized",
        )


def require_active_state(game: models.Game) -> None:
    if game.status != "active":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Game is not active yet",
        )


def validate_turn_order(players: list[models.Player], player_ids: list[int]) -> None:
    if not players:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Game has no players")
    if len(player_ids) != len(set(player_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Turn order contains duplicates")

    player_id_set = {player.id for player in players}
    if set(player_ids) != player_id_set:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Turn order must include every player exactly once",
        )


def validate_finalize_setup(players: list[models.Player]) -> None:
    if not players:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Game must have at least one player")
    seat_orders = [player.seat_order for player in players]
    if len(seat_orders) != len(set(seat_orders)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Turn order must be unique")


def validate_suggestion_player(players: list[models.Player], suggester_id: int) -> None:
    player_ids = {player.id for player in players}
    if suggester_id not in player_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Suggester not found in this game")


def validate_showing(
    suggestion: Optional[models.Suggestion],
    game_id: int,
    players: list[models.Player],
    showing_player_id: int,
    existing_showing: Optional[models.Showing],
) -> None:
    if not suggestion or suggestion.game_id != game_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Suggestion not found for this game")

    if existing_showing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Suggestion already has a showing")

    player_ids = {player.id for player in players}
    if showing_player_id not in player_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Showing player not found in this game")
