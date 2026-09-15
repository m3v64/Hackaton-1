from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserDataCreate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


class UserDataOut(UserDataCreate):
    user_id: str
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    id: str
    email: EmailStr
    password: str
    data: UserDataCreate | None = None


class UserOut(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime | None = None
    data: UserDataOut | None = None
    model_config = ConfigDict(from_attributes=True)


class CourseCreate(BaseModel):
    name: str


class CourseOut(CourseCreate):
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class PlannedCourseCreate(BaseModel):
    course_name: str
    planned_date: datetime | None = None
    assigned_at: datetime | None = None


class PlannedCourseOut(PlannedCourseCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class MembershipCreate(BaseModel):
    class_name: str


class MembershipOut(MembershipCreate):
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class MembershipCardCreate(BaseModel):
    id: str
    membership_class: str
    user_id: str
    courses_included: bool = False
    personal_trainings_included: bool = False
    assigned_at: datetime | None = None


class MembershipCardOut(MembershipCardCreate):
    model_config = ConfigDict(from_attributes=True)


class PersonalTrainingCreate(BaseModel):
    user_id: str
    coach_id: str
    date_planned: datetime


class PersonalTrainingOut(PersonalTrainingCreate):
    model_config = ConfigDict(from_attributes=True)
