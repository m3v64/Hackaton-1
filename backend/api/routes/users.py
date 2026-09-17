from fastapi import APIRouter, status

from api.schemas.models import ActionResponse, UserCreate, UserData, UserOut, UserUpdate

router = APIRouter()


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate) -> UserOut:
    return UserOut(user_id=body.user_id, **body.model_dump(exclude={"user_id"}))


@router.get("/users", response_model=list[UserOut])
def list_users() -> list[UserOut]:
    return [UserOut(user_id="user-001")]


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str) -> UserOut:
    return UserOut(user_id=user_id)


@router.post("/{user_id}/cancel", response_model=ActionResponse)
def cancel_user(user_id: str) -> ActionResponse:
    return ActionResponse(success=True, message=f"User {user_id} membership cancelled and account deleted.")
