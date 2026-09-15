from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, EmailStr
from src.api.db.models.enums import UserRole


class User(BaseModel):
    id: int
    username: str
    password: str
    email : EmailStr
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    username: str | None = None
    role: UserRole | None = None
    avatar: str | None = None
    email: EmailStr | None = None
    password: str | None = None
