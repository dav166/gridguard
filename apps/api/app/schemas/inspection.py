from datetime import date, datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.models.inspection import (
    InspectionResult,
    InspectionStatus,
    InspectionType,
)


class InspectionCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    title: str = Field(
        min_length=2,
        max_length=160,
    )

    inspection_type: InspectionType

    inspection_date: date

    notes: str | None = Field(
        default=None,
        max_length=4000,
    )


class InspectionUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=160,
    )

    inspection_type: InspectionType | None = None

    inspection_date: date | None = None

    notes: str | None = Field(
        default=None,
        max_length=4000,
    )


class InspectionSubmitRequest(BaseModel):
    result: InspectionResult

    notes: str | None = Field(
        default=None,
        max_length=4000,
    )


class InspectionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    organization_id: UUID
    project_id: UUID
    title: str
    inspection_type: InspectionType
    inspection_date: date
    status: InspectionStatus
    result: InspectionResult | None
    notes: str | None
    performed_by_user_id: UUID | None
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime
