from __future__ import annotations

from datetime import datetime
from api.db.models.enums import Action, MembershipType, CourseType

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())

    data: Mapped[UserData | None] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    roles: Mapped[list[UserRole]] = relationship(back_populates="user", cascade="all, delete-orphan")
    planned_courses: Mapped[list[UserPlannedCourse]] = relationship(back_populates="user", cascade="all, delete-orphan")
    membership_cards: Mapped[list[MembershipCard]] = relationship(back_populates="user", cascade="all, delete-orphan")
    planned_trainings: Mapped[list[PersonalTraining]] = relationship(
        back_populates="user", foreign_keys="PersonalTraining.user_id", cascade="all, delete-orphan"
    )
    coached_trainings: Mapped[list[PersonalTraining]] = relationship(
        back_populates="coach", foreign_keys="PersonalTraining.coach_id"
    )


class UserData(Base):
    __tablename__ = "usersdata"

    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    first_name: Mapped[str | None] = mapped_column("firstname", String(50))
    last_name: Mapped[str | None] = mapped_column("lastname", String(50))
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())

    user: Mapped[User] = relationship(back_populates="data")


class PlannedCourse(Base):
    __tablename__ = "plannedCourses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course: Mapped[CourseType] = mapped_column("CourseType", nullable=False)
    planned_date: Mapped[datetime | None] = mapped_column("plannedDate", DateTime, unique=True)
    assigned_at: Mapped[datetime | None] = mapped_column("assignedAt", DateTime)

    users: Mapped[list[UserPlannedCourse]] = relationship(back_populates="planned_course_record")


class UserPlannedCourse(Base):
    __tablename__ = "userPlannedCourses"

    planned_course: Mapped[str] = mapped_column(
        "plannedCourses", ForeignKey("plannedCourses.coursesName"), primary_key=True
    )
    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    assigned_at: Mapped[datetime | None] = mapped_column("assignedAt", DateTime)

    planned_course_record: Mapped[PlannedCourse] = relationship(
        back_populates="users", foreign_keys=[planned_course]
    )
    user: Mapped[User] = relationship(back_populates="planned_courses")


class MembershipCard(Base):
    __tablename__ = "membershipCards"
    __table_args__ = (UniqueConstraint("membershipClass", "userId", name="uq_membershipCards_class_user"),)

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    membership_type: Mapped[MembershipType] = mapped_column("MembershipType", nullable=False, default=False)
    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    courses_included: Mapped[bool] = mapped_column("coursesIncluded", nullable=False, default=False)
    personal_trainings_included: Mapped[bool] = mapped_column("personalTrainingsIncluded", nullable=False, default=False)
    assigned_at: Mapped[datetime | None] = mapped_column("assignedAt", DateTime)

    user: Mapped[User] = relationship(back_populates="membership_cards")


class PersonalTraining(Base):
    __tablename__ = "personalTrainings"

    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id"), primary_key=True)
    coach_id: Mapped[str] = mapped_column("coachId", ForeignKey("users.id"), primary_key=True)
    date_planned: Mapped[datetime] = mapped_column("datePlanned", DateTime, primary_key=True)

    user: Mapped[User] = relationship(back_populates="planned_trainings", foreign_keys=[user_id])
    coach: Mapped[User] = relationship(back_populates="coached_trainings", foreign_keys=[coach_id])


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column("roleName", String(30), nullable=False)
    description: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())

    users: Mapped[list[UserRole]] = relationship(back_populates="role", cascade="all, delete-orphan")
    permissions: Mapped[list[RolePermission]] = relationship(back_populates="role", cascade="all, delete-orphan")


class UserRole(Base):
    __tablename__ = "userRoles"
    __table_args__ = (UniqueConstraint("userId", name="uq_userRoles_userId"),)

    role_id: Mapped[int] = mapped_column("roleId", ForeignKey("roles.id"), primary_key=True)
    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    assigned_at: Mapped[datetime | None] = mapped_column("assignedAt", DateTime)

    role: Mapped[Role] = relationship(back_populates="users")
    user: Mapped[User] = relationship(back_populates="roles")


class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = (UniqueConstraint("resource", "action", name="uq_permissions_resource_action"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resource: Mapped[str] = mapped_column(String(30), nullable=False)
    action: Mapped[Action] = mapped_column(Enum(Action), nullable=False)
    description: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())

    roles: Mapped[list[RolePermission]] = relationship(back_populates="permission", cascade="all, delete-orphan")


class RolePermission(Base):
    __tablename__ = "rolePermissions"

    role_id: Mapped[int] = mapped_column("roleId", ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column("permissionId", ForeignKey("permissions.id"), primary_key=True)
    assigned_at: Mapped[datetime | None] = mapped_column("assignedAt", DateTime)

    role: Mapped[Role] = relationship(back_populates="permissions")
    permission: Mapped[Permission] = relationship(back_populates="roles")