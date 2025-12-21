from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, root_validator
from pydantic.types import conint


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class GameBase(BaseModel):
    name: str


class GameCreate(GameBase):
    pass


class GameOut(GameBase):
    id: int
    status: str
    created_at: datetime
    owner_id: Optional[int]

    class Config:
        orm_mode = True


class PlayerBase(BaseModel):
    name: str
    seat_order: conint(ge=1)


class PlayerCreate(PlayerBase):
    pass


class PlayerOut(PlayerBase):
    id: int
    game_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class GameDetail(GameOut):
    players: List[PlayerOut] = []


class HandBase(BaseModel):
    game_id: int
    player_id: int


class HandCreate(HandBase):
    pass


class HandOut(HandBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class EnvelopeBase(BaseModel):
    game_id: int


class EnvelopeCreate(EnvelopeBase):
    pass


class EnvelopeOut(EnvelopeBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class CardBase(BaseModel):
    name: str
    card_type: str


class CardCreate(CardBase):
    game_id: int
    hand_id: Optional[int] = None
    envelope_id: Optional[int] = None
    is_unknown: bool = True

    @root_validator
    def validate_single_location(cls, values):
        location_flags = [
            values.get("hand_id") is not None,
            values.get("envelope_id") is not None,
            bool(values.get("is_unknown")),
        ]
        if sum(location_flags) != 1:
            raise ValueError("Card must belong to exactly one location.")
        return values


class CardOut(CardBase):
    id: int
    game_id: int
    hand_id: Optional[int]
    envelope_id: Optional[int]
    is_unknown: bool
    created_at: datetime

    class Config:
        orm_mode = True


class SuggestionBase(BaseModel):
    game_id: int
    player_id: int
    suspect_card_id: int
    weapon_card_id: int
    room_card_id: int


class SuggestionCreate(SuggestionBase):
    pass


class SuggestionOut(SuggestionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class ShowingBase(BaseModel):
    suggestion_id: int
    player_id: int
    card_id: int


class ShowingCreate(ShowingBase):
    pass


class ShowingOut(ShowingBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class TurnOrderBase(BaseModel):
    game_id: int
    player_id: int
    turn_index: conint(ge=1)


class TurnOrderCreate(TurnOrderBase):
    pass


class TurnOrderOut(TurnOrderBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class SimulationOverride(BaseModel):
    player_id: int
    strategy_key: str


class SimulationRequest(BaseModel):
    user_player_id: int
    user_strategy: str = "conservative"
    opponent_strategy: str = "random"
    iterations: conint(ge=1, le=1000) = 100
    rounds: conint(ge=1, le=50) = 5
    include_timeline: bool = False
    strategy_overrides: List[SimulationOverride] = []


class SimulationAssignmentOut(BaseModel):
    player_id: int
    name: str
    strategy_key: str
    is_user: bool


class SimulationResponse(BaseModel):
    iterations: int
    rounds: int
    user_player_id: int
    user_strategy: str
    opponent_strategy: str
    user_win_percentage: float
    strategy_win_percentages: dict
    strategy_win_counts: dict
    assignments: List[SimulationAssignmentOut]
    timeline: Optional[List[dict]] = None
