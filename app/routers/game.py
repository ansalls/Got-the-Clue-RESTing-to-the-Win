from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, oauth2
from ..database import get_db
from ..services import game_validation


router = APIRouter(
    prefix="/games",
    tags=["Games"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.GameOut)
def create_game(
    game: schemas.GameCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    new_game = models.Game(name=game.name, owner_id=current_user.id)
    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    return new_game


@router.get("/", response_model=List[schemas.GameOut])
def list_games(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    return db.query(models.Game).filter(models.Game.owner_id == current_user.id).order_by(models.Game.created_at.desc()).all()


@router.get("/{game_id}", response_model=schemas.GameDetail)
def get_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    game = game_validation.require_game_exists(
        db.query(models.Game).filter(models.Game.id == game_id).first()
    )
    if game.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this game")
    return game


@router.post("/{game_id}/players", status_code=status.HTTP_201_CREATED, response_model=schemas.PlayerOut)
def add_player(
    game_id: int,
    player: schemas.PlayerCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    game = game_validation.require_game_exists(
        db.query(models.Game).filter(models.Game.id == game_id).first()
    )
    game_validation.require_game_owner(game, current_user)
    game_validation.require_setup_state(game)

    existing_player = db.query(models.Player).filter(
        models.Player.game_id == game_id,
        models.Player.seat_order == player.seat_order,
    ).first()
    if existing_player:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seat order already taken for this game",
        )

    new_player = models.Player(game_id=game_id, name=player.name, seat_order=player.seat_order)
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player


@router.get("/{game_id}/players", response_model=List[schemas.PlayerOut])
def list_players(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    game = game_validation.require_game_exists(
        db.query(models.Game).filter(models.Game.id == game_id).first()
    )
    if game.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this game")
    return db.query(models.Player).filter(models.Player.game_id == game_id).order_by(models.Player.seat_order.asc()).all()


@router.put("/{game_id}/turn-order", response_model=List[schemas.PlayerOut])
def set_turn_order(
    game_id: int,
    payload: schemas.TurnOrderUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    game = game_validation.require_game_exists(
        db.query(models.Game).filter(models.Game.id == game_id).first()
    )
    game_validation.require_game_owner(game, current_user)
    game_validation.require_setup_state(game)

    players = db.query(models.Player).filter(models.Player.game_id == game_id).all()
    game_validation.validate_turn_order(players, payload.player_ids)

    order_map = {player_id: index + 1 for index, player_id in enumerate(payload.player_ids)}
    for player in players:
        player.seat_order = order_map[player.id]

    db.commit()
    return db.query(models.Player).filter(models.Player.game_id == game_id).order_by(models.Player.seat_order.asc()).all()


@router.post("/{game_id}/finalize", response_model=schemas.GameOut)
def finalize_setup(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    game = game_validation.require_game_exists(
        db.query(models.Game).filter(models.Game.id == game_id).first()
    )
    game_validation.require_game_owner(game, current_user)
    game_validation.require_setup_state(game)

    players = db.query(models.Player).filter(models.Player.game_id == game_id).all()
    game_validation.validate_finalize_setup(players)

    # We lock setup here to preserve consistency for suggestion logging.
    game.status = "active"
    db.commit()
    db.refresh(game)
    return game


@router.post("/{game_id}/suggestions", status_code=status.HTTP_201_CREATED, response_model=schemas.SuggestionOut)
def create_suggestion(
    game_id: int,
    payload: schemas.SuggestionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    game = game_validation.require_game_exists(
        db.query(models.Game).filter(models.Game.id == game_id).first()
    )
    game_validation.require_game_owner(game, current_user)
    game_validation.require_active_state(game)

    players = db.query(models.Player).filter(models.Player.game_id == game_id).all()
    game_validation.validate_suggestion_player(players, payload.suggester_id)

    suggestion = models.Suggestion(
        game_id=game_id,
        suggester_id=payload.suggester_id,
        suspect=payload.suspect,
        weapon=payload.weapon,
        room=payload.room,
    )
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    return suggestion


@router.post("/{game_id}/showings", status_code=status.HTTP_201_CREATED, response_model=schemas.ShowingOut)
def create_showing(
    game_id: int,
    payload: schemas.ShowingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    game = game_validation.require_game_exists(
        db.query(models.Game).filter(models.Game.id == game_id).first()
    )
    game_validation.require_game_owner(game, current_user)
    game_validation.require_active_state(game)

    suggestion = db.query(models.Suggestion).filter(models.Suggestion.id == payload.suggestion_id).first()
    existing_showing = db.query(models.Showing).filter(
        models.Showing.suggestion_id == payload.suggestion_id
    ).first()
    players = db.query(models.Player).filter(models.Player.game_id == game_id).all()
    game_validation.validate_showing(
        suggestion,
        game_id,
        players,
        payload.showing_player_id,
        existing_showing,
    )

    showing = models.Showing(
        game_id=game_id,
        suggestion_id=payload.suggestion_id,
        showing_player_id=payload.showing_player_id,
        shown_card=payload.shown_card,
    )
    db.add(showing)
    db.commit()
    db.refresh(showing)
    return showing
