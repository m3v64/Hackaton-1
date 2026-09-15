from __future__ import annotations
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.core.env import env
from src.api.core.deps import DbDep
from src.api.core.security import create_access_token, hash_password, verify_password
from api.db.models.user import User
from src.api.schemas.auth import GoogleAuthRequest, LoginRequest, RegisterRequest, TokenResponse
from src.api.schemas.common import ApiResponse


router = APIRouter(prefix="/auth")

def _issue_token(user: User) -> TokenResponse:
    token = create_access_token(
        subject=user.id,
        extra={"role": user.role.value},
    )
    return TokenResponse(
        access_token=token,
        expires_in=env.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def _lookup_user_by_email_or_name(db, identifier: str) -> User | None:
    user = db.query(User).filter(User.email == identifier).first()
    if user is None:
        user = db.query(User).filter(User.username == identifier).first()
    return user


@router.post("/login", response_model=ApiResponse[TokenResponse], summary="Log in with username/email + password")
def login(body: LoginRequest, db: DbDep) -> ApiResponse[TokenResponse]:
    user = _lookup_user_by_email_or_name(db, body.identifier)
    if user is None or user.password is None or not verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled.")
    return ApiResponse(result=_issue_token(user))


@router.post("/login/form", response_model=ApiResponse[TokenResponse], summary="OAuth2 password-flow endpoint", include_in_schema=False)
def login_form(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbDep) -> ApiResponse[TokenResponse]:
    user = _lookup_user_by_email_or_name(db, form.username)
    if user is None or user.password is None or not verify_password(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled.")
    return ApiResponse(result=_issue_token(user))


@router.post("/register", response_model=ApiResponse[TokenResponse], status_code=status.HTTP_201_CREATED, summary="Create a new account")
def register(body: RegisterRequest, db: DbDep) -> ApiResponse[TokenResponse]:
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken.")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")

    user = User(
        username=body.username,
        email=body.email,
        display_name=body.display_name,
        password=hash_password(body.password),
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return ApiResponse(result=_issue_token(user))


@router.post("/google", response_model=ApiResponse[TokenResponse], summary="Sign in / register with a Google account")
async def google_auth(body: GoogleAuthRequest, db: DbDep) -> ApiResponse[TokenResponse]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": body.id_token},
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token.",
        )

    info = resp.json()

    if env.GOOGLE_CLIENT_ID and info.get("aud") != env.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google token mismatch.",
        )

    google_id: str = info["sub"]
    email: str = info.get("email", "")
    display_name: str | None = info.get("name")
    avatar: str | None = info.get("picture")

    user = db.query(User).filter(User.google_id == google_id).first()
    if user is None and email:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.google_id = google_id

    if user is None:
        base = email.split("@")[0].replace(".", "_")[:28]
        username = base
        suffix = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base}_{suffix}"
            suffix += 1

        user = User(
            google_id=google_id,
            username=username,
            email=email,
            display_name=display_name,
            avatar=avatar or "/default-avatar.png",
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled.")

    return ApiResponse(result=_issue_token(user))
