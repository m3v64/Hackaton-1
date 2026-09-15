from datetime import datetime, timedelta

from api.core.security import hash_password
from api.db.models.enums import Action
from api.db.models.hackaton import (
    Course,
    Membership,
    MembershipCard,
    Permission,
    PersonalTraining,
    PlannedCourse,
    Role,
    RolePermission,
    User,
    UserData,
    UserPlannedCourse,
    UserRole,
)


BASE_DATE = datetime(2026, 9, 21, 18, 0)


def user_factory(
    user_id: str,
    email: str,
    first_name: str,
    last_name: str,
    password: str = "demo1234",
) -> User:
    return User(
        id=user_id,
        email=email,
        password=hash_password(password),
        data=UserData(first_name=first_name, last_name=last_name),
    )


def course_factory(name: str) -> Course:
    return Course(name=name)


def planned_course_factory(course_name: str, offset_days: int) -> PlannedCourse:
    return PlannedCourse(
        course_name=course_name,
        planned_date=BASE_DATE + timedelta(days=offset_days),
        assigned_at=BASE_DATE,
    )


def membership_factory(class_name: str) -> Membership:
    return Membership(class_name=class_name)


def membership_card_factory(
    card_id: str,
    membership_class: str,
    user_id: str,
    *,
    courses_included: bool = False,
    personal_trainings_included: bool = False,
) -> MembershipCard:
    return MembershipCard(
        id=card_id,
        membership_class=membership_class,
        user_id=user_id,
        courses_included=courses_included,
        personal_trainings_included=personal_trainings_included,
        assigned_at=BASE_DATE,
    )


def personal_training_factory(user_id: str, coach_id: str, offset_days: int) -> PersonalTraining:
    return PersonalTraining(
        user_id=user_id,
        coach_id=coach_id,
        date_planned=BASE_DATE + timedelta(days=offset_days, hours=1),
    )


def role_factory(role_name: str, description: str) -> Role:
    return Role(role_name=role_name, description=description)


def permission_factory(resource: str, action: Action, description: str) -> Permission:
    return Permission(resource=resource, action=action, description=description)


def user_role_factory(role_id: int, user_id: str) -> UserRole:
    return UserRole(role_id=role_id, user_id=user_id, assigned_at=BASE_DATE)


def role_permission_factory(role_id: int, permission_id: int) -> RolePermission:
    return RolePermission(role_id=role_id, permission_id=permission_id, assigned_at=BASE_DATE)


def user_planned_course_factory(planned_course: str, user_id: str) -> UserPlannedCourse:
    return UserPlannedCourse(
        planned_course=planned_course,
        user_id=user_id,
        assigned_at=BASE_DATE,
    )
