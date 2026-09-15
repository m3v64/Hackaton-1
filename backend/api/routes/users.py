from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.db.models.hackaton import User, UserData
from api.db.session import get_db
from api.schemas.models import UserCreate, UserOut

router = APIRouter(prefix="/users")


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, db: Session = Depends(get_db)) -> User:
    if db.get(User, body.id) or db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="User already exists.")

    user = User(id=body.id, email=body.email, password=body.password)
    if body.data:
        user.data = UserData(
            user_id=body.id,
            first_name=body.data.first_name,
            last_name=body.data.last_name,
        )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user
