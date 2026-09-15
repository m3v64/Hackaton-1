from __future__ import annotations

import argparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.db.base import Base
from api.db.factories import (
    course_factory,
    membership_card_factory,
    membership_factory,
    personal_training_factory,
    planned_course_factory,
    permission_factory,
    role_factory,
    role_permission_factory,
    user_factory,
    user_planned_course_factory,
    user_role_factory,
)
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
    UserPlannedCourse,
    UserRole,
)
from api.db.session import SessionLocal, engine


COURSE_NAMES = ("Yoga", "Pilates", "Paaldansen")
MEMBERSHIP_NAMES = ("1x per week", "2x per week", "Onbeperkt", "Cursus addendum")


def _add_if_missing(db: Session, model: type, identity: object, factory):
    existing = db.get(model, identity)
    if existing is not None:
        return existing
    record = factory()
    db.add(record)
    db.flush()
    return record


def seed(db: Session, reset: bool = False) -> None:
    if reset:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    users = {
        "member-001": _add_if_missing(
            db, User, "member-001", lambda: user_factory("member-001", "sanne@example.com", "Sanne", "Jansen")
        ),
        "member-002": _add_if_missing(
            db, User, "member-002", lambda: user_factory("member-002", "milan@example.com", "Milan", "de Boer")
        ),
        "coach-001": _add_if_missing(
            db, User, "coach-001", lambda: user_factory("coach-001", "coach@example.com", "Noor", "Visser")
        ),
        "reception-001": _add_if_missing(
            db, User, "reception-001", lambda: user_factory("reception-001", "receptie@example.com", "Ravi", "Smit")
        ),
    }

    courses = {
        name: _add_if_missing(db, Course, name, lambda name=name: course_factory(name))
        for name in COURSE_NAMES
    }
    memberships = {
        name: _add_if_missing(db, Membership, name, lambda name=name: membership_factory(name))
        for name in MEMBERSHIP_NAMES
    }

    roles = {}
    for role_name, description in (
        ("member", "Can access the gym and manage personal bookings"),
        ("coach", "Can manage personal training appointments"),
        ("reception", "Can manage members, memberships and courses"),
    ):
        role = db.scalar(select(Role).where(Role.role_name == role_name))
        if role is None:
            role = role_factory(role_name, description)
            db.add(role)
            db.flush()
        roles[role_name] = role

    permissions = {}
    for resource, action, description in (
        ("access", Action.READ, "Allow gym access checks"),
        ("courses", Action.CREATE, "Create course bookings"),
        ("memberships", Action.UPDATE, "Update membership access"),
        ("trainings", Action.CREATE, "Schedule personal training"),
    ):
        permission = db.scalar(
            select(Permission).where(Permission.resource == resource, Permission.action == action)
        )
        if permission is None:
            permission = permission_factory(resource, action, description)
            db.add(permission)
            db.flush()
        permissions[(resource, action)] = permission

    role_permission_pairs = (
        ("member", ("access", Action.READ)),
        ("member", ("courses", Action.CREATE)),
        ("coach", ("trainings", Action.CREATE)),
        ("reception", ("access", Action.READ)),
        ("reception", ("courses", Action.CREATE)),
        ("reception", ("memberships", Action.UPDATE)),
        ("reception", ("trainings", Action.CREATE)),
    )
    for role_name, permission_key in role_permission_pairs:
        key = (roles[role_name].id, permissions[permission_key].id)
        if db.get(RolePermission, key) is None:
            db.add(role_permission_factory(*key))

    for role_name, user_id in (
        ("member", "member-001"),
        ("member", "member-002"),
        ("coach", "coach-001"),
        ("reception", "reception-001"),
    ):
        key = (roles[role_name].id, user_id)
        if db.get(UserRole, key) is None:
            db.add(user_role_factory(*key))

    for membership_name, user_id, card_id, courses_included, trainings_included in (
        ("1x per week", "member-001", "card-001", False, False),
        ("Cursus addendum", "member-001", "card-002", True, False),
        ("Onbeperkt", "member-002", "card-003", False, True),
    ):
        if db.get(MembershipCard, card_id) is None:
            db.add(
                membership_card_factory(
                    card_id,
                    membership_name,
                    user_id,
                    courses_included=courses_included,
                    personal_trainings_included=trainings_included,
                )
            )

    planned_courses = {}
    for name, offset in zip(COURSE_NAMES, (0, 1, 2)):
        planned = db.scalar(select(PlannedCourse).where(PlannedCourse.course_name == name))
        if planned is None:
            planned = planned_course_factory(name, offset)
            db.add(planned)
            db.flush()
        planned_courses[name] = planned

    for course_name, user_id in (("Yoga", "member-001"), ("Pilates", "member-002")):
        key = (course_name, user_id)
        if db.get(UserPlannedCourse, key) is None:
            db.add(user_planned_course_factory(*key))

    training_key = ("member-001", "coach-001", planned_courses["Yoga"].planned_date.replace(hour=19))
    if db.get(PersonalTraining, training_key) is None:
        db.add(personal_training_factory("member-001", "coach-001", 0))

    db.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Hackaton 1 demo data.")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables before seeding.")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed(db, reset=args.reset)
    print("Hackaton 1 demo data seeded successfully.")


if __name__ == "__main__":
    main()
