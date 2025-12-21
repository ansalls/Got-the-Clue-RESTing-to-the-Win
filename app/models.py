from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    owner_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('CURRENT_TIMESTAMP'))


class Vote(Base):
    __tablename__ = "votes"
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey(
        "posts.id", ondelete="CASCADE"), primary_key=True)


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, server_default="setup")
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    owner_id = Column(Integer, ForeignKey(
        "users.id", ondelete="SET NULL"), nullable=True)

    owner = relationship("User")
    players = relationship("Player", back_populates="game",
                           cascade="all, delete-orphan")


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(Integer, ForeignKey(
        "games.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    seat_order = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    game = relationship("Game", back_populates="players")


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)


class PlayerCard(Base):
    __tablename__ = "player_cards"

    id = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(Integer, ForeignKey(
        "games.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(Integer, ForeignKey(
        "players.id", ondelete="CASCADE"), nullable=False)
    card_id = Column(Integer, ForeignKey(
        "cards.id", ondelete="CASCADE"), nullable=False)

    player = relationship("Player")
    card = relationship("Card")


class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(Integer, ForeignKey(
        "games.id", ondelete="CASCADE"), nullable=False)
    suggester_id = Column(Integer, ForeignKey(
        "players.id", ondelete="CASCADE"), nullable=False)
    suspect_card_id = Column(Integer, ForeignKey(
        "cards.id", ondelete="CASCADE"), nullable=False)
    weapon_card_id = Column(Integer, ForeignKey(
        "cards.id", ondelete="CASCADE"), nullable=False)
    room_card_id = Column(Integer, ForeignKey(
        "cards.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    suggester = relationship("Player")
    suspect_card = relationship("Card", foreign_keys=[suspect_card_id])
    weapon_card = relationship("Card", foreign_keys=[weapon_card_id])
    room_card = relationship("Card", foreign_keys=[room_card_id])


class SuggestionResponse(Base):
    __tablename__ = "suggestion_responses"

    id = Column(Integer, primary_key=True, nullable=False)
    suggestion_id = Column(Integer, ForeignKey(
        "suggestions.id", ondelete="CASCADE"), nullable=False)
    shower_id = Column(Integer, ForeignKey(
        "players.id", ondelete="SET NULL"), nullable=True)
    shown_card_id = Column(Integer, ForeignKey(
        "cards.id", ondelete="SET NULL"), nullable=True)

    suggestion = relationship("Suggestion")
    shower = relationship("Player")
    shown_card = relationship("Card")
