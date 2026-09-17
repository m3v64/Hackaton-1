from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserData(BaseModel):
    first_name: str = "Alex"
    last_name: str = "Example"
    email: EmailStr = "alex@example.com"
    phone: str = "+1 555 0100"


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class UserOut(UserData):
    user_id: str
    membership_type: str = "unlimited"


class UserCreate(UserData):
    user_id: str


class MembershipUpdate(BaseModel):
    membership_type: str


class MembershipOut(BaseModel):
    user_id: str
    membership_type: str
    active: bool = True


class GateRequest(BaseModel):
    membership_card_id: str


class GateResponse(BaseModel):
    allowed: bool


class PersonalTrainingRequest(BaseModel):
    coached: str
    user_id: str
    time_slot: datetime


class PersonalTrainingSlot(BaseModel):
    coach_id: str
    coach_name: str
    time_slot: datetime
    available: bool = True


class CourseEnrollmentRequest(BaseModel):
    user_id: str


class CourseSlot(BaseModel):
    course_id: str
    course_name: str
    time_slot: datetime
    available: bool = True


class PlannedCourse(BaseModel):
    course_id: str
    course_name: str
    time_slot: datetime


class ActionResponse(BaseModel):
    success: bool
    message: str


class CourseCreate(BaseModel):
    name: str


class CourseOut(BaseModel):
    course_id: str
    name: str
    time_slots: list[datetime] = []


class PlannedCourseCreate(BaseModel):
    course_name: str
    planned_date: datetime | None = None


class PlannedCourseOut(PlannedCourse):
    pass


class MembershipCreate(BaseModel):
    membership_type: str


class MembershipCardCreate(BaseModel):
    id: str
    membership_type: str
    user_id: str


class MembershipCardOut(MembershipCardCreate):
    active: bool = True


class PersonalTrainingCreate(PersonalTrainingRequest):
    pass


class PersonalTrainingOut(PersonalTrainingRequest):
    success: bool = True
