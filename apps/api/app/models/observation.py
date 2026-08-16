from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    Uuid,
    false,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ObservationKind(StrEnum):
    SAFE_PRACTICE = "safe_practice"
    UNSAFE_CONDITION = "unsafe_condition"
    UNSAFE_BEHAVIOR = "unsafe_behavior"
    NEAR_MISS = "near_miss"


class ObservationCategory(StrEnum):
    HOUSEKEEPING = "housekeeping"
    PPE = "ppe"
    FALL_PROTECTION = "fall_protection"
    ELECTRICAL = "electrical"
    EQUIPMENT = "equipment"
    EXCAVATION = "excavation"
    LIFTING_RIGGING = "lifting_rigging"
    ENVIRONMENTAL = "environmental"
    FIRE_PREVENTION = "fire_prevention"
    ACCESS_EGRESS = "access_egress"
    OTHER = "other"


class ObservationSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SafetyObservation(Base):
    __tablename__ = "safety_observations"

    __table_args__ = (
        CheckConstraint(
            ("kind IN ('safe_practice', 'unsafe_condition', 'unsafe_behavior', 'near_miss')"),
            name="ck_safety_observations_kind",
        ),
        CheckConstraint(
            (
                "category IN ("
                "'housekeeping', "
                "'ppe', "
                "'fall_protection', "
                "'electrical', "
                "'equipment', "
                "'excavation', "
                "'lifting_rigging', "
                "'environmental', "
                "'fire_prevention', "
                "'access_egress', "
                "'other'"
                ")"
            ),
            name="ck_safety_observations_category",
        ),
        CheckConstraint(
            ("severity IS NULL OR severity IN ('low', 'medium', 'high', 'critical')"),
            name="ck_safety_observations_severity",
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

    kind: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    severity: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
    )

    location: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    immediate_action_taken: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    requires_corrective_action: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false(),
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
