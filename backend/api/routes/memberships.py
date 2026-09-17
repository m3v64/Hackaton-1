from datetime import datetime

from fastapi import APIRouter

from api.schemas.models import (
    GateRequest,
    GateResponse,
    ActionResponse,
    MembershipOut,
    MembershipUpdate,
    PersonalTrainingRequest,
    PersonalTrainingSlot,
    UserData,
)

router = APIRouter()


@router.post("/gate", response_model=GateResponse)
def check_gate(body: GateRequest) -> GateResponse:
    allowed = body.membership_card_id != "denied"
    return GateResponse(allowed=allowed, reason="Access approved." if allowed else "Access denied.")


@router.get("/{user_id}/membership", response_model=MembershipOut)
def get_membership(user_id: str) -> MembershipOut:
    return MembershipOut(user_id=user_id, membership_type="unlimited")


@router.post("/{user_id}/membership", response_model=MembershipOut)
def set_membership(user_id: str, body: MembershipUpdate) -> MembershipOut:
    return MembershipOut(user_id=user_id, membership_type=body.membership_type)


@router.get("/memberships", response_model=list[MembershipOut])
def list_memberships() -> list[MembershipOut]:
    return [MembershipOut(user_id="user-001", membership_type="unlimited")]


@router.post("/personal-training", response_model=ActionResponse)
def book_personal_training(body: PersonalTrainingRequest) -> ActionResponse:
    return ActionResponse(success=True, message=f"Training with {body.coached} booked for {body.time_slot}.")


@router.get("/personal-training", response_model=list[PersonalTrainingSlot])
def list_personal_training() -> list[PersonalTrainingSlot]:
    return [
        PersonalTrainingSlot(
            coach_id="coach-001",
            coach_name="Jamie Coach",
            time_slot=datetime(2026, 10, 1, 10, 0),
        )
    ]
