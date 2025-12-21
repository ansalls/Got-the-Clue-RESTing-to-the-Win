from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, oauth2, knowledge
from ..database import get_db


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
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
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
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    if game.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this game")

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
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    if game.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this game")
    return db.query(models.Player).filter(models.Player.game_id == game_id).order_by(models.Player.seat_order.asc()).all()


@router.get("/{game_id}/knowledge", response_model=schemas.GameKnowledgeOut)
def get_game_knowledge(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    if game.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this game")

    snapshot = knowledge.build_game_knowledge(db, game_id)
    cards_by_id = {card.id: card for card in db.query(models.Card).all()}

    def card_ref(card_id: int) -> schemas.CardRef:
        card = cards_by_id[card_id]
        return schemas.CardRef(id=card.id, name=card.name, category=card.category)

    return schemas.GameKnowledgeOut(
        cards=[
            schemas.CardKnowledgeOut(
                id=card.card_id,
                name=card.name,
                category=card.category,
                owner_player_id=card.owner_player_id,
                owner_known=card.owner_known,
            )
            for card in snapshot.cards
        ],
        players=[
            schemas.PlayerKnowledgeOut(
                player_id=player.player_id,
                name=player.name,
                confirmed_cards=[card_ref(card_id) for card_id in player.confirmed_card_ids],
                possible_cards=[card_ref(card_id) for card_id in player.possible_card_ids],
            )
            for player in snapshot.players
        ],
        envelope_possibilities=schemas.EnvelopePossibilitiesOut(
            suspects=[card_ref(card_id) for card_id in snapshot.envelope.suspects],
            weapons=[card_ref(card_id) for card_id in snapshot.envelope.weapons],
            rooms=[card_ref(card_id) for card_id in snapshot.envelope.rooms],
        ),
    )
