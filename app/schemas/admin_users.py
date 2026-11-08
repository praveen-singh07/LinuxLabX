from typing import Literal

from pydantic import BaseModel, ConfigDict


class AdminUserItem(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class AdminUserList(BaseModel):
    items: list[AdminUserItem]
    total: int
    limit: int
    offset: int


class AdminUserStatusWrite(BaseModel):
    is_active: bool


class AdminUserRoleWrite(BaseModel):
    role: Literal["student", "admin"]


class AdminOverview(BaseModel):
    users_total: int
    users_active: int
    users_suspended: int
    learning_paths: int
    lessons: int
    quizzes: int
    practice_exercises: int
    challenges: int
