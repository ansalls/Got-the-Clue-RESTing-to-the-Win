from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

from pydantic.types import conint


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: Post
    votes: int

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


class Vote(BaseModel):
    post_id: int
    dir: conint(ge=0, le=1)


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
