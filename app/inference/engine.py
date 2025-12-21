from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Set


class KnowledgeType(str, Enum):
    HAS_CARD = "has_card"
    DOES_NOT_HAVE_CARD = "does_not_have_card"


@dataclass(frozen=True)
class CardKnowledge:
    player: str
    card: str
    knowledge: KnowledgeType


@dataclass
class CardInferenceEngine:
    _has_cards: Dict[str, Set[str]] = field(default_factory=dict)
    _not_cards: Dict[str, Set[str]] = field(default_factory=dict)

    def record_card_shown(self, player: str, card: str) -> None:
        if card in self._not_cards.get(player, set()):
            raise ValueError(
                f"Conflicting deduction: {player} cannot both have and not have {card}."
            )
        self._has_cards.setdefault(player, set()).add(card)

    def record_cannot_show(self, player: str, cards: Iterable[str]) -> None:
        for card in cards:
            if card in self._has_cards.get(player, set()):
                raise ValueError(
                    f"Conflicting deduction: {player} already confirmed holding {card}."
                )
            self._not_cards.setdefault(player, set()).add(card)

    def knowledge_for_player(self, player: str) -> List[CardKnowledge]:
        has_cards = [
            CardKnowledge(player=player, card=card, knowledge=KnowledgeType.HAS_CARD)
            for card in sorted(self._has_cards.get(player, set()))
        ]
        not_cards = [
            CardKnowledge(
                player=player,
                card=card,
                knowledge=KnowledgeType.DOES_NOT_HAVE_CARD,
            )
            for card in sorted(self._not_cards.get(player, set()))
        ]
        return has_cards + not_cards

    def all_knowledge(self) -> List[CardKnowledge]:
        players = set(self._has_cards.keys()) | set(self._not_cards.keys())
        combined: List[CardKnowledge] = []
        for player in sorted(players):
            combined.extend(self.knowledge_for_player(player))
        return combined
