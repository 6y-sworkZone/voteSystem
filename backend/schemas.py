from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class OptionBase(BaseModel):
    text: str


class OptionCreate(OptionBase):
    pass


class OptionResponse(OptionBase):
    id: int
    vote_count: int = 0
    percentage: float = 0.0

    class Config:
        from_attributes = True


class PollBase(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: datetime


class PollCreate(PollBase):
    options: List[OptionCreate]


class PollResponse(PollBase):
    id: int
    created_at: datetime
    creator_id: int
    options: List[OptionResponse]
    total_votes: int = 0
    is_expired: bool = False
    has_voted: bool = False
    voted_option_id: Optional[int] = None

    class Config:
        from_attributes = True


class VoteCreate(BaseModel):
    option_id: int


class VoteResponse(BaseModel):
    id: int
    poll_id: int
    option_id: int
    created_at: datetime

    class Config:
        from_attributes = True
