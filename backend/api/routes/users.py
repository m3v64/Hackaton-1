from __future__ import annotations
from typing import Annotated, Union

from fastapi import APIRouter, HTTPException, Path, Query, status

from src.api.core.deps import CurrentUser, DbDep
from api.core.privacy import assert_can_view_user, build_user_profile
from src.api.core.security import hash_password
from api.db.models.following import Following
from api.db.models.notification import Notification
from api.db.models.post import Post, SavedPost
from api.db.models.user import User
from api.schemas.media import MediaOut
from src.api.schemas.common import ApiResponse, PaginatedResult
from api.schemas.notification import NotificationOut
from api.schemas.post import PostOut, TagOut
from src.api.schemas.user import UserPublic, UserPrivate, UserUpdateRequest


router = APIRouter(prefix="/users")

def _get_user_by_id(db, user_id: int) -> User:
    user = db.get(User, user_id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    return user


def _get_user_by_username(db, username: str) -> User:
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    return user


def _assert_owner_or_admin(current_user: User, target_user: User) -> None:
    from src.api.db.models.enums import UserRole
    
    if current_user.id != target_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")


@router.get("/{user_id}", response_model=ApiResponse[Union[UserPrivate, UserPublic, UserPrivate]], summary="Get user profile by ID")
def get_user_by_id(user_id: Annotated[int, Path(description="Numeric user ID")], db: DbDep, current_user: CurrentUser) -> ApiResponse:
    user = _get_user_by_id(db, user_id)

    if current_user.id == user.id:
        return ApiResponse(result=UserPrivate.model_validate(user))

    return ApiResponse(result=build_user_profile(db, current_user, user))


@router.get("/index/{username}", response_model=ApiResponse[Union[UserPrivate, UserPublic, UserPrivate]], summary="Get user profile by username")
def get_user_by_username(username: Annotated[str, Path(description="Unique username")], db: DbDep, current_user: CurrentUser) -> ApiResponse:
    user = _get_user_by_username(db, username)

    if current_user.id == user.id:
        return ApiResponse(result=UserPrivate.model_validate(user))

    return ApiResponse(result=build_user_profile(db, current_user, user))


@router.patch("/{user_id}", response_model=ApiResponse[UserPrivate], summary="Update a user's profile")
def update_user_by_id(user_id: Annotated[int, Path()], body: UserUpdateRequest, db: DbDep, current_user: CurrentUser) -> ApiResponse[UserPrivate]:
    user = _get_user_by_id(db, user_id)
    _assert_owner_or_admin(current_user, user)

    for field, value in body.model_dump(exclude_none=True).items():
        if field == "password":
            value = hash_password(value)
            
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return ApiResponse(result=UserPrivate.model_validate(user))


@router.delete("/{user_id}", response_model=ApiResponse[None], status_code=status.HTTP_200_OK, summary="Delete a user account")
def delete_user_by_id(user_id: Annotated[int, Path()], db: DbDep, current_user: CurrentUser) -> ApiResponse[None]:
    user = _get_user_by_id(db, user_id)
    _assert_owner_or_admin(current_user, user)
    
    db.delete(user)
    db.commit()
    return ApiResponse(result=None)


@router.get("/{user_id}/following", response_model=ApiResponse[PaginatedResult[UserPrivate]], summary="List users that this user follows")
def get_following(user_id: Annotated[int, Path()], db: DbDep, current_user: CurrentUser, offset: Annotated[int, Query(ge=0)] = 0, limit: Annotated[int, Query(ge=1, le=100)] = 20) -> ApiResponse[PaginatedResult[UserPrivate]]:
    user = _get_user_by_id(db, user_id)
    assert_can_view_user(db, current_user, user)

    rows = (
        db.query(Following)
        .filter(Following.follower_id == user.id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    total = db.query(Following).filter(Following.follower_id == user.id).count()
    items = [UserPrivate.model_validate(r.following_user) for r in rows]
    return ApiResponse(result=PaginatedResult(items=items, total=total, offset=offset, limit=limit))


@router.get("/{user_id}/followers", response_model=ApiResponse[PaginatedResult[UserPrivate]], summary="List users that follow this user")
def get_followers(user_id: Annotated[int, Path()], db: DbDep, current_user: CurrentUser, offset: Annotated[int, Query(ge=0)] = 0, limit: Annotated[int, Query(ge=1, le=100)] = 20) -> ApiResponse[PaginatedResult[UserPrivate]]:
    user = _get_user_by_id(db, user_id)
    assert_can_view_user(db, current_user, user)

    rows = (
        db.query(Following)
        .filter(Following.following_id == user.id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    total = db.query(Following).filter(Following.following_id == user.id).count()
    items = [UserPrivate.model_validate(r.follower) for r in rows]
    return ApiResponse(result=PaginatedResult(items=items, total=total, offset=offset, limit=limit))


@router.post("/{user_id}/follow", response_model=ApiResponse[None], status_code=status.HTTP_201_CREATED, summary="Follow a user")
def follow_user(user_id: Annotated[int, Path()], db: DbDep, current_user: CurrentUser) -> ApiResponse[None]:
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself.")
    
    _get_user_by_id(db, user_id)
    existing = (
        db.query(Following)
        .filter(Following.follower_id == current_user.id, Following.following_id == user_id)
        .first()
    )
    
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already following.")
    
    db.add(Following(follower_id=current_user.id, following_id=user_id))
    db.commit()
    return ApiResponse(result=None)


@router.delete("/{user_id}/follow", response_model=ApiResponse[None], summary="Unfollow a user")
def unfollow_user(user_id: Annotated[int, Path()], db: DbDep, current_user: CurrentUser) -> ApiResponse[None]:
    row = (
        db.query(Following)
        .filter(Following.follower_id == current_user.id, Following.following_id == user_id)
        .first()
    )
    
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not following.")
    
    db.delete(row)
    db.commit()
    return ApiResponse(result=None)


@router.get("/{user_id}/posts", response_model=ApiResponse[PaginatedResult[PostOut]], summary="List posts by a user")
def get_user_posts(user_id: Annotated[int, Path()], db: DbDep, current_user: CurrentUser, offset: Annotated[int, Query(ge=0)] = 0, limit: Annotated[int, Query(ge=1, le=100)] = 20) -> ApiResponse[PaginatedResult[PostOut]]:
    user = _get_user_by_id(db, user_id)
    assert_can_view_user(db, current_user, user)

    query = db.query(Post).filter(Post.user_id == user_id)
    total = query.count()
    posts = query.order_by(Post.created_at.desc()).offset(offset).limit(limit).all()
    items = [_build_post_out(p) for p in posts]
    return ApiResponse(result=PaginatedResult(items=items, total=total, offset=offset, limit=limit))


@router.get("/{user_id}/saved", response_model=ApiResponse[PaginatedResult[PostOut]], summary="List a user's saved posts (owner/admin only)")
def get_saved_posts(user_id: Annotated[int, Path()], db: DbDep, current_user: CurrentUser, offset: Annotated[int, Query(ge=0)] = 0, limit: Annotated[int, Query(ge=1, le=100)] = 20) -> ApiResponse[PaginatedResult[PostOut]]:
    user = _get_user_by_id(db, user_id)
    _assert_owner_or_admin(current_user, user)

    query = (
        db.query(SavedPost)
        .filter(SavedPost.user_id == user_id)
    )
    
    total = query.count()
    rows = query.offset(offset).limit(limit).all()
    items = [_build_post_out(r.post) for r in rows]
    return ApiResponse(result=PaginatedResult(items=items, total=total, offset=offset, limit=limit))


@router.get("/{user_id}/notifications", response_model=ApiResponse[PaginatedResult[NotificationOut]], summary="List notifications for a user")
def get_notifications(user_id: Annotated[int, Path()], db: DbDep, current_user: CurrentUser, offset: Annotated[int, Query(ge=0)] = 0, limit: Annotated[int, Query(ge=1, le=100)] = 20, unread_only: Annotated[bool, Query()] = False) -> ApiResponse[PaginatedResult[NotificationOut]]:
    user = _get_user_by_id(db, user_id)
    _assert_owner_or_admin(current_user, user)

    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))

    total = query.count()
    notifs = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    items = [NotificationOut.model_validate(n) for n in notifs]
    return ApiResponse(result=PaginatedResult(items=items, total=total, offset=offset, limit=limit))


@router.post("/{user_id}/notifications/read-all", response_model=ApiResponse[None], summary="Mark all notifications as read")
def mark_all_read(user_id: Annotated[int, Path()], db: DbDep, current_user: CurrentUser) -> ApiResponse[None]:
    user = _get_user_by_id(db, user_id)
    _assert_owner_or_admin(current_user, user)
    
    (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read.is_(False))
        .update({"is_read": True})
    )
    
    db.commit()
    return ApiResponse(result=None)


def _build_post_out(post: Post) -> PostOut:
    return PostOut(
        id=post.id,
        user=UserPrivate.model_validate(post.user),
        title=post.title,
        description=post.description,
        like_count=len(post.likes),
        comment_count=len(post.comments),
        tags=[TagOut.model_validate(pt.tag) for pt in post.tags],
        media=[MediaOut.model_validate(m) for m in post.media],
        created_at=post.created_at,
        updated_at=post.updated_at,
    )