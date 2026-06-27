from pydantic import BaseModel
from typing import Optional


class ChallengeCreate(BaseModel):

    title: str
    slug: str
    description: str
    category: str
    difficulty: str

    xp_reward: int = 100
    estimated_minutes: int = 15

    command_required: Optional[str] = None


class ChallengeResponse(BaseModel):

    id: int
    title: str
    slug: str
    description: str
    category: str
    difficulty: str

    xp_reward: int
    estimated_minutes: int

    command_required: Optional[str]

    is_active: bool

    class Config:
        from_attributes = True