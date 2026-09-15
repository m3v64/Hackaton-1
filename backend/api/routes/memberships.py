from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.db.models.hackaton import Membership, MembershipCard, PersonalTraining, User
from api.db.session import get_db
from api.schemas.models import (
    MembershipCardCreate,
    MembershipCardOut,
    MembershipCreate,
    MembershipOut,
    PersonalTrainingCreate,
    PersonalTrainingOut,
)

router = APIRouter(prefix="/memberships")


@router.post("", response_model=MembershipOut, status_code=status.HTTP_201_CREATED)
def create_membership(body: MembershipCreate, db: Session = Depends(get_db)) -> Membership:
    if db.get(Membership, body.class_name):
        raise HTTPException(status_code=409, detail="Membership already exists.")
    membership = Membership(class_name=body.class_name)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


@router.post("/cards", response_model=MembershipCardOut, status_code=status.HTTP_201_CREATED)
def create_membership_card(body: MembershipCardCreate, db: Session = Depends(get_db)) -> MembershipCard:
    if not db.get(Membership, body.membership_class):
        raise HTTPException(status_code=404, detail="Membership not found.")
    if not db.get(User, body.user_id):
        raise HTTPException(status_code=404, detail="User not found.")
    card = MembershipCard(**body.model_dump())
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


@router.post("/trainings", response_model=PersonalTrainingOut, status_code=status.HTTP_201_CREATED)
def create_personal_training(body: PersonalTrainingCreate, db: Session = Depends(get_db)) -> PersonalTraining:
    if not db.get(User, body.user_id) or not db.get(User, body.coach_id):
        raise HTTPException(status_code=404, detail="Training user or coach not found.")
    training = PersonalTraining(**body.model_dump())
    db.add(training)
    db.commit()
    db.refresh(training)
    return training
