from pydantic import BaseModel
from typing import Optional


class UserProfileResponse(BaseModel):

    id: int
    username: str
    email: str

    full_name: Optional[str]

    avatar: Optional[str]

    bio: Optional[str]

    xp: int
    level: int
    streak: int

    is_active: bool

    class Config:
        from_attributes = True