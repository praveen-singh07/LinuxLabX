from pydantic import BaseModel
from pydantic import EmailStr

from typing import Optional


class RegisterRequest(BaseModel):

    username: str

    email: EmailStr

    password: str

    full_name: Optional[str] = None


class LoginRequest(BaseModel):

    email: EmailStr

    password: str


class Token(BaseModel):

    access_token: str

    token_type: str


class TokenData(BaseModel):

    email: Optional[str] = None


class UserResponse(BaseModel):

    id: int

    username: str

    email: str

    full_name: Optional[str]

    xp: int

    level: int

    streak: int


    class Config:

        from_attributes = True