from datetime import date, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InspectionType(StrEnum):
    GENERAL_SITE = "general_site"
    DAILY_SITE = "daily_site"
    WEEKLY_SITE = "weekly_site"
    PRE_TASK = "pre_task"
    EQUIPMENT = "equipment"
    ELECTRICAL = "electrical"
    ENVIRONMENTAL = "environmental"
    OTHER = "other"


class InspectionStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"


class InspectionResult(StrEnum):
    SATISFACTORY = "satisfactory"
    NEEDS_ATTENTION = "needs_attention"
    CRITICAL = "critical"


class Inspection(Base):
    __tablename__ = "inspections"

    __table_args__ = (
        CheckConstraint(
            (
                "inspection_type IN ("
                "'general_site', "
                "'daily_site', "
                "'weekly_site', "
                "'pre_task', "
                "'equipment', "
                "'electrical', "
                "'environmental', "
                "'other'"
                ")"
            ),
            name="ck_inspections_type",
        ),
        CheckConstraint(
            "status IN ('draft', 'submitted')",
            name="ck_inspections_status",
        ),
        CheckConstraint(
            ("result IS NULL OR result IN ('satisfactory', 'needs_attention', 'critical')"),
            name="ck_inspections_result",
        ),
        CheckConstraint(
            (
                "(status = 'draft' AND submitted_at IS NULL) "
                "OR "
                "("
                "status = 'submitted' "
                "AND submitted_at IS NOT NULL "
                "AND result IS NOT NULL"
                ")"
            ),
            name="ck_inspections_submission_state",
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

    project_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )

    inspection_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    inspection_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="draft",
    )

    result: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    performed_by_user_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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
