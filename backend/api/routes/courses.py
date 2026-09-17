from datetime import datetime

from fastapi import APIRouter

from api.schemas.models import ActionResponse, CourseSlot, PlannedCourse, UserOut, UserUpdate

router = APIRouter()


@router.post("/{resource_id}", response_model=UserOut | ActionResponse)
def update_user_or_enroll(resource_id: str, body: dict) -> UserOut | ActionResponse:
    if "user_id" in body:
        return ActionResponse(success=True, message=f"User {body['user_id']} enrolled in {resource_id}.")

    update = UserUpdate.model_validate(body)
    return UserOut(user_id=resource_id, **update.model_dump(exclude_none=True))


@router.get("/planned-courses", response_model=list[CourseSlot])
def list_planned_courses() -> list[CourseSlot]:
    return [
        CourseSlot(
            course_id="course-001",
            course_name="Yoga",
            time_slot=datetime(2026, 10, 2, 18, 0),
        )
    ]


@router.get("/{user_id}/planned-courses", response_model=list[PlannedCourse])
def list_user_planned_courses(user_id: str) -> list[PlannedCourse]:
    return [
        PlannedCourse(
            course_id="course-001",
            course_name="Yoga",
            time_slot=datetime(2026, 10, 2, 18, 0),
        )
    ]
