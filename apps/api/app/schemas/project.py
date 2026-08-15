from datetime import date, datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.models.project import (
    ProjectStatus,
    ProjectType,
)


class ProjectCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    name: str = Field(
        min_length=2,
        max_length=160,
    )

    code: str = Field(
        min_length=2,
        max_length=40,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$",
    )

    project_type: ProjectType

    location: str = Field(
        min_length=2,
        max_length=160,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    start_date: date | None = None
    end_date: date | None = None

    @field_validator("code")
    @classmethod
    def normalize_code(
        cls,
        code: str,
    ) -> str:
        return code.upper()

    @model_validator(mode="after")
    def validate_date_range(
        self,
    ) -> "ProjectCreate":
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError("end_date must be on or after start_date")

        return self


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=160,
    )

    code: str | None = Field(
        default=None,
        min_length=2,
        max_length=40,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$",
    )

    project_type: ProjectType | None = None
    status: ProjectStatus | None = None

    location: str | None = Field(
        default=None,
        min_length=2,
        max_length=160,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    start_date: date | None = None
    end_date: date | None = None

    @field_validator("code")
    @classmethod
    def normalize_code(
        cls,
        code: str | None,
    ) -> str | None:
        if code is None:
            return None

        return code.upper()


class ProjectResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    organization_id: UUID
    name: str
    code: str
    project_type: ProjectType
    status: ProjectStatus
    location: str
    description: str | None
    start_date: date | None
    end_date: date | None
    created_by_user_id: UUID | None
    created_at: datetime
    updated_at: datetime
