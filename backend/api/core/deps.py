from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from api.core.security import decode_access_token
from api.db.session import get_db
from api.db.models.hackaton import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)

DbDep = Annotated[Session, Depends(get_db)]


def _get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbDep) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")

    user = db.get(User, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive.")

    return user


def _get_optional_user(token: Annotated[str | None, Depends(oauth2_scheme_optional)], db: DbDep) -> User | None:
    if not token:
        return None

    payload = decode_access_token(token)
    if not payload:
        return None

    user = db.get(User, payload.get("sub"))
    if not user or not user.is_active:
        return None

    return user


CurrentUser = Annotated[User, Depends(_get_current_user)]
OptionalCurrentUser = Annotated[User | None, Depends(_get_optional_user)]