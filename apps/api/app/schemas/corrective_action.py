from datetime import date, datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.models.corrective_action import (
    CorrectiveActionPriority,
    CorrectiveActionStatus,
)


class CorrectiveActionCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    observation_id: UUID

    title: str = Field(
        min_length=2,
        max_length=160,
    )

    description: str = Field(
        min_length=2,
        max_length=4000,
    )

    priority: CorrectiveActionPriority

    assigned_to_user_id: UUID

    due_date: date


class CorrectiveActionUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=160,
    )

    description: str | None = Field(
        default=None,
        min_length=2,
        max_length=4000,
    )

    priority: CorrectiveActionPriority | None = None

    assigned_to_user_id: UUID | None = None

    due_date: date | None = None


class CorrectiveActionCompleteRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    completion_notes: str = Field(
        min_length=2,
        max_length=4000,
    )


class CorrectiveActionVerifyRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    verification_notes: str | None = Field(
        default=None,
        max_length=4000,
    )


class CorrectiveActionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    organization_id: UUID
    project_id: UUID
    inspection_id: UUID
    observation_id: UUID

    title: str
    description: str

    priority: CorrectiveActionPriority
    status: CorrectiveActionStatus

    assigned_to_user_id: UUID | None
    due_date: date

    completion_notes: str | None
    completed_by_user_id: UUID | None
    completed_at: datetime | None

    verification_notes: str | None
    verified_by_user_id: UUID | None
    verified_at: datetime | None

    created_by_user_id: UUID | None

    created_at: datetime
    updated_at: datetime
