from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, server_default="setup")
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    owner = relationship("User")
    players = relationship(
        "Player",
        back_populates="game",
        cascade="all, delete-orphan",
    )
    hands = relationship(
        "Hand",
        back_populates="game",
        cascade="all, delete-orphan",
    )
    envelope = relationship(
        "Envelope",
        back_populates="game",
        uselist=False,
        cascade="all, delete-orphan",
    )
    cards = relationship(
        "Card",
        back_populates="game",
        cascade="all, delete-orphan",
    )
    suggestions = relationship(
        "Suggestion",
        back_populates="game",
        cascade="all, delete-orphan",
    )
    turn_orders = relationship(
        "TurnOrder",
        back_populates="game",
        cascade="all, delete-orphan",
    )


class Player(Base):
    __tablename__ = "players"
    __table_args__ = (
        UniqueConstraint("game_id", "seat_order", name="uq_players_game_seat_order"),
    )

    id = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    seat_order = Column(Integer, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    game = relationship("Game", back_populates="players")
    hand = relationship(
        "Hand",
        back_populates="player",
        uselist=False,
        cascade="all, delete-orphan",
    )
    suggestions = relationship(
        "Suggestion",
        back_populates="player",
        cascade="all, delete-orphan",
    )
    showings = relationship(
        "Showing",
        back_populates="player",
        cascade="all, delete-orphan",
    )
    turn_orders = relationship(
        "TurnOrder",
        back_populates="player",
        cascade="all, delete-orphan",
    )


class Hand(Base):
    __tablename__ = "hands"
    __table_args__ = (
        UniqueConstraint("player_id", name="uq_hands_player"),
    )

    id = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    game = relationship("Game", back_populates="hands")
    player = relationship("Player", back_populates="hand")
    cards = relationship(
        "Card",
        back_populates="hand",
        cascade="all, delete-orphan",
    )


class Envelope(Base):
    __tablename__ = "envelopes"
    __table_args__ = (
        UniqueConstraint("game_id", name="uq_envelopes_game"),
    )

    id = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    game = relationship("Game", back_populates="envelope")
    cards = relationship(
        "Card",
        back_populates="envelope",
        cascade="all, delete-orphan",
    )


class Card(Base):
    __tablename__ = "cards"
    __table_args__ = (
        UniqueConstraint("game_id", "name", name="uq_cards_game_name"),
        # Preserve clue state by requiring every card to live in exactly one place.
        CheckConstraint(
            "(CASE WHEN hand_id IS NOT NULL THEN 1 ELSE 0 END) + "
            "(CASE WHEN envelope_id IS NOT NULL THEN 1 ELSE 0 END) + "
            "(CASE WHEN is_unknown THEN 1 ELSE 0 END) = 1",
            name="ck_cards_single_location",
        ),
    )

    id = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    card_type = Column(String, nullable=False)
    hand_id = Column(Integer, ForeignKey("hands.id", ondelete="SET NULL"), nullable=True)
    envelope_id = Column(Integer, ForeignKey("envelopes.id", ondelete="SET NULL"), nullable=True)
    is_unknown = Column(Boolean, nullable=False, server_default=text("TRUE"))
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    game = relationship("Game", back_populates="cards")
    hand = relationship("Hand", back_populates="cards")
    envelope = relationship("Envelope", back_populates="cards")
    suspect_suggestions = relationship(
        "Suggestion",
        back_populates="suspect_card",
        foreign_keys="Suggestion.suspect_card_id",
    )
    weapon_suggestions = relationship(
        "Suggestion",
        back_populates="weapon_card",
        foreign_keys="Suggestion.weapon_card_id",
    )
    room_suggestions = relationship(
        "Suggestion",
        back_populates="room_card",
        foreign_keys="Suggestion.room_card_id",
    )
    showings = relationship("Showing", back_populates="card", cascade="all, delete-orphan")


class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    suspect_card_id = Column(Integer, ForeignKey("cards.id", ondelete="RESTRICT"), nullable=False)
    weapon_card_id = Column(Integer, ForeignKey("cards.id", ondelete="RESTRICT"), nullable=False)
    room_card_id = Column(Integer, ForeignKey("cards.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    game = relationship("Game", back_populates="suggestions")
    player = relationship("Player", back_populates="suggestions")
    suspect_card = relationship("Card", foreign_keys=[suspect_card_id], back_populates="suspect_suggestions")
    weapon_card = relationship("Card", foreign_keys=[weapon_card_id], back_populates="weapon_suggestions")
    room_card = relationship("Card", foreign_keys=[room_card_id], back_populates="room_suggestions")
    showings = relationship(
        "Showing",
        back_populates="suggestion",
        cascade="all, delete-orphan",
    )


class Showing(Base):
    __tablename__ = "showings"

    id = Column(Integer, primary_key=True, nullable=False)
    suggestion_id = Column(Integer, ForeignKey("suggestions.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    card_id = Column(Integer, ForeignKey("cards.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    suggestion = relationship("Suggestion", back_populates="showings")
    player = relationship("Player", back_populates="showings")
    card = relationship("Card", back_populates="showings")


class TurnOrder(Base):
    __tablename__ = "turn_orders"
    __table_args__ = (
        UniqueConstraint("game_id", "turn_index", name="uq_turn_orders_game_turn_index"),
        UniqueConstraint("game_id", "player_id", name="uq_turn_orders_game_player"),
    )

    id = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    turn_index = Column(Integer, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    game = relationship("Game", back_populates="turn_orders")
    player = relationship("Player", back_populates="turn_orders")
