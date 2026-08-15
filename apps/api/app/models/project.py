from datetime import date, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProjectType(StrEnum):
    SOLAR = "solar"
    WIND = "wind"
    BATTERY_STORAGE = "battery_storage"
    TRANSMISSION = "transmission"
    SUBSTATION = "substation"
    OTHER = "other"


class ProjectStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    __tablename__ = "projects"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "code",
            name="uq_projects_organization_code",
        ),
        CheckConstraint(
            (
                "project_type IN ("
                "'solar', "
                "'wind', "
                "'battery_storage', "
                "'transmission', "
                "'substation', "
                "'other'"
                ")"
            ),
            name="ck_projects_project_type",
        ),
        CheckConstraint(
            (
                "status IN ("
                "'planned', "
                "'active', "
                "'on_hold', "
                "'completed', "
                "'archived'"
                ")"
            ),
            name="ck_projects_status",
        ),
        CheckConstraint(
            (
                "end_date IS NULL "
                "OR start_date IS NULL "
                "OR end_date >= start_date"
            ),
            name="ck_projects_date_range",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )

    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    project_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="planned",
    )

    location: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    created_by_user_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )