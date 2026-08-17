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


class CorrectiveActionPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CorrectiveActionStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"


class CorrectiveAction(Base):
    __tablename__ = "corrective_actions"

    __table_args__ = (
        CheckConstraint(
            ("priority IN ('low', 'medium', 'high', 'critical')"),
            name="ck_corrective_actions_priority",
        ),
        CheckConstraint(
            ("status IN ('open', 'in_progress', 'completed', 'verified')"),
            name="ck_corrective_actions_status",
        ),
        CheckConstraint(
            (
                "("
                "status IN ('open', 'in_progress') "
                "AND completed_at IS NULL "
                "AND completed_by_user_id IS NULL "
                "AND completion_notes IS NULL "
                "AND verified_at IS NULL "
                "AND verified_by_user_id IS NULL"
                ") OR ("
                "status = 'completed' "
                "AND completed_at IS NOT NULL "
                "AND completed_by_user_id IS NOT NULL "
                "AND completion_notes IS NOT NULL "
                "AND verified_at IS NULL "
                "AND verified_by_user_id IS NULL"
                ") OR ("
                "status = 'verified' "
                "AND completed_at IS NOT NULL "
                "AND completed_by_user_id IS NOT NULL "
                "AND completion_notes IS NOT NULL "
                "AND verified_at IS NOT NULL "
                "AND verified_by_user_id IS NOT NULL"
                ")"
            ),
            name="ck_corrective_actions_workflow_state",
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

    inspection_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey(
            "inspections.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    observation_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey(
            "safety_observations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="open",
    )

    assigned_to_user_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    completion_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    completed_by_user_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    verification_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    verified_by_user_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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
