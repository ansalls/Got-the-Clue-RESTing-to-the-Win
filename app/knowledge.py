from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set

from sqlalchemy.orm import Session

from . import models


@dataclass(frozen=True)
class CardKnowledge:
    card_id: int
    name: str
    category: str
    owner_player_id: Optional[int]
    owner_known: bool


@dataclass(frozen=True)
class PlayerKnowledge:
    player_id: int
    name: str
    confirmed_card_ids: List[int]
    possible_card_ids: List[int]


@dataclass(frozen=True)
class EnvelopePossibilities:
    suspects: List[int]
    weapons: List[int]
    rooms: List[int]


@dataclass(frozen=True)
class KnowledgeSnapshot:
    cards: List[CardKnowledge]
    players: List[PlayerKnowledge]
    envelope: EnvelopePossibilities


def _build_known_owners(
    player_cards: Iterable[models.PlayerCard],
    responses: Iterable[models.SuggestionResponse],
) -> Dict[int, int]:
    known_owners: Dict[int, int] = {}
    for player_card in player_cards:
        known_owners[player_card.card_id] = player_card.player_id
    for response in responses:
        if response.shown_card_id and response.shower_id:
            known_owners[response.shown_card_id] = response.shower_id
    return known_owners


def _build_possible_cards_by_player(
    responses: Iterable[models.SuggestionResponse],
) -> Dict[int, Set[int]]:
    possible_cards: Dict[int, Set[int]] = {}
    for response in responses:
        if response.shower_id and response.shown_card_id is None:
            suggestion = response.suggestion
            possible_cards.setdefault(response.shower_id, set()).update(
                [
                    suggestion.suspect_card_id,
                    suggestion.weapon_card_id,
                    suggestion.room_card_id,
                ]
            )
    return possible_cards


def build_game_knowledge(db: Session, game_id: int) -> KnowledgeSnapshot:
    players = (
        db.query(models.Player)
        .filter(models.Player.game_id == game_id)
        .order_by(models.Player.seat_order.asc())
        .all()
    )
    cards = db.query(models.Card).order_by(models.Card.id.asc()).all()
    player_cards = (
        db.query(models.PlayerCard)
        .filter(models.PlayerCard.game_id == game_id)
        .all()
    )
    responses = (
        db.query(models.SuggestionResponse)
        .join(models.Suggestion)
        .filter(models.Suggestion.game_id == game_id)
        .all()
    )

    known_owners = _build_known_owners(player_cards, responses)
    possible_cards_by_player = _build_possible_cards_by_player(responses)
    for card_id, owner_id in known_owners.items():
        for player_id, possible_cards in possible_cards_by_player.items():
            if player_id != owner_id:
                possible_cards.discard(card_id)

    cards_by_id = {card.id: card for card in cards}

    card_knowledge: List[CardKnowledge] = [
        CardKnowledge(
            card_id=card.id,
            name=card.name,
            category=card.category,
            owner_player_id=known_owners.get(card.id),
            owner_known=card.id in known_owners,
        )
        for card in cards
    ]

    player_knowledge: List[PlayerKnowledge] = []
    for player in players:
        confirmed = sorted(
            card_id for card_id, owner_id in known_owners.items() if owner_id == player.id
        )
        possible = sorted(
            card_id
            for card_id in possible_cards_by_player.get(player.id, set())
            if card_id not in confirmed
        )
        player_knowledge.append(
            PlayerKnowledge(
                player_id=player.id,
                name=player.name,
                confirmed_card_ids=confirmed,
                possible_card_ids=possible,
            )
        )

    def _by_category(category: str) -> List[int]:
        return sorted(
            card.id for card in cards if card.category == category and card.id not in known_owners
        )

    envelope = EnvelopePossibilities(
        suspects=_by_category("suspect"),
        weapons=_by_category("weapon"),
        rooms=_by_category("room"),
    )

    return KnowledgeSnapshot(
        cards=card_knowledge,
        players=player_knowledge,
        envelope=envelope,
    )
