from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.models.observation import (
    ObservationCategory,
    ObservationKind,
    ObservationSeverity,
)


class ObservationCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    kind: ObservationKind
    category: ObservationCategory

    severity: ObservationSeverity | None = None

    location: str = Field(
        min_length=2,
        max_length=160,
    )

    description: str = Field(
        min_length=2,
        max_length=4000,
    )

    immediate_action_taken: str | None = Field(
        default=None,
        max_length=4000,
    )

    requires_corrective_action: bool = False

    @model_validator(mode="after")
    def validate_observation(
        self,
    ) -> "ObservationCreate":
        if self.kind == ObservationKind.SAFE_PRACTICE:
            if self.severity is not None:
                raise ValueError("Safe practices cannot have a hazard severity.")

            if self.requires_corrective_action:
                raise ValueError("Safe practices cannot require corrective action.")

        elif self.severity is None:
            raise ValueError("Unsafe observations require a severity.")

        return self


class ObservationUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    category: ObservationCategory | None = None

    severity: ObservationSeverity | None = None

    location: str | None = Field(
        default=None,
        min_length=2,
        max_length=160,
    )

    description: str | None = Field(
        default=None,
        min_length=2,
        max_length=4000,
    )

    immediate_action_taken: str | None = Field(
        default=None,
        max_length=4000,
    )

    requires_corrective_action: bool | None = None


class ObservationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    organization_id: UUID
    project_id: UUID
    inspection_id: UUID

    kind: ObservationKind
    category: ObservationCategory
    severity: ObservationSeverity | None

    location: str
    description: str
    immediate_action_taken: str | None

    requires_corrective_action: bool

    created_by_user_id: UUID | None

    created_at: datetime
    updated_at: datetime
