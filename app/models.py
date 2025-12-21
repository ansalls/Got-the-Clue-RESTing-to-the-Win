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
    suggestions = relationship("Suggestion", back_populates="game",
                               cascade="all, delete-orphan")
    showings = relationship("Showing", back_populates="game",
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
    suggestions = relationship("Suggestion", back_populates="suggester",
                               cascade="all, delete-orphan")
    showings = relationship("Showing", back_populates="showing_player",
                            cascade="all, delete-orphan")


class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(Integer, ForeignKey(
        "games.id", ondelete="CASCADE"), nullable=False)
    suggester_id = Column(Integer, ForeignKey(
        "players.id", ondelete="CASCADE"), nullable=False)
    suspect = Column(String, nullable=False)
    weapon = Column(String, nullable=False)
    room = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    game = relationship("Game", back_populates="suggestions")
    suggester = relationship("Player", back_populates="suggestions")
    showings = relationship("Showing", back_populates="suggestion",
                            cascade="all, delete-orphan")


class Showing(Base):
    __tablename__ = "showings"

    id = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(Integer, ForeignKey(
        "games.id", ondelete="CASCADE"), nullable=False)
    suggestion_id = Column(Integer, ForeignKey(
        "suggestions.id", ondelete="CASCADE"), nullable=False)
    showing_player_id = Column(Integer, ForeignKey(
        "players.id", ondelete="CASCADE"), nullable=False)
    shown_card = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    game = relationship("Game", back_populates="showings")
    suggestion = relationship("Suggestion", back_populates="showings")
    showing_player = relationship("Player", back_populates="showings")
