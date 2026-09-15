from __future__ import annotations

from datetime import datetime
from src.api.db.models.enums import Action

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())

    data: Mapped[UserData | None] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    roles: Mapped[list[UserRole]] = relationship(back_populates="user", cascade="all, delete-orphan")
    planned_courses: Mapped[list[UserPlannedCourse]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserData(Base):
    __tablename__ = "usersdata"

    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    first_name: Mapped[str | None] = mapped_column("firstname", String(50))
    last_name: Mapped[str | None] = mapped_column("lastname", String(50))
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())

    user: Mapped[User] = relationship(back_populates="data")


class Course(Base):
    __tablename__ = "courses"

    name: Mapped[str] = mapped_column(String(100), primary_key=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())

    planned_courses: Mapped[list[PlannedCourse]] = relationship(back_populates="course")


class PlannedCourse(Base):
    __tablename__ = "plannedCourses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_name: Mapped[str] = mapped_column("coursesName", ForeignKey("courses.name"), nullable=False)
    planned_date: Mapped[datetime | None] = mapped_column("plannedDate", DateTime, unique=True)
    assigned_at: Mapped[datetime | None] = mapped_column("assignedAt", DateTime)

    course: Mapped[Course] = relationship(back_populates="planned_courses")
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


class Membership(Base):
    __tablename__ = "memberships"

    class_name: Mapped[str] = mapped_column("class", String(255), primary_key=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())

    cards: Mapped[list[MembershipCard]] = relationship(back_populates="membership")


class MembershipCard(Base):
    __tablename__ = "membershipCards"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    membership_class: Mapped[str | None] = mapped_column("membershipClass", ForeignKey("memberships.class"))

    membership: Mapped[Membership | None] = relationship(back_populates="cards")


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