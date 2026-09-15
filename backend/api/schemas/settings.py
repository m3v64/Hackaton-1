from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel
from src.api.db.models.enums import PrivacyMode


class UserSettingsOut(BaseModel):
    user_id: int
    privacy: PrivacyMode
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserSettingsUpdateRequest(BaseModel):
    privacy: PrivacyMode | None = None