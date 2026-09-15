from __future__ import annotations
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status

from src.api.core.deps import CurrentUser, DbDep
from src.api.db.models.enums import UserRole
from api.db.models.user import User, UserSettings
from src.api.schemas.common import ApiResponse
from src.api.schemas.settings import UserSettingsOut, UserSettingsUpdateRequest


router = APIRouter(prefix="/users")


def _get_user_or_404(db, user_id: int) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return user


def _get_or_create_settings(db, user_id: int) -> UserSettings:
    settings = db.get(UserSettings, user_id)
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


def _assert_owner_or_admin(current_user: User, target_user_id: int) -> None:
    if current_user.id != target_user_id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")


@router.get("/{user_id}/settings", response_model=ApiResponse[UserSettingsOut], summary="Get a user's settings (owner/admin only)")
def get_user_settings(user_id: Annotated[int, Path()], db: DbDep, current_user: CurrentUser) -> ApiResponse[UserSettingsOut]:
    _get_user_or_404(db, user_id)
    _assert_owner_or_admin(current_user, user_id)

    settings = _get_or_create_settings(db, user_id)
    return ApiResponse(result=UserSettingsOut.model_validate(settings))


@router.patch("/{user_id}/settings", response_model=ApiResponse[UserSettingsOut], summary="Update a user's settings (owner/admin only)")
def update_user_settings(user_id: Annotated[int, Path()], body: UserSettingsUpdateRequest, db: DbDep, current_user: CurrentUser) -> ApiResponse[UserSettingsOut]:
    _get_user_or_404(db, user_id)
    _assert_owner_or_admin(current_user, user_id)

    settings = _get_or_create_settings(db, user_id)

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(settings, field, value)

    db.commit()
    db.refresh(settings)
    return ApiResponse(result=UserSettingsOut.model_validate(settings))