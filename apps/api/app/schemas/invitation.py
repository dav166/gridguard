from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from app.models.membership import OrganizationRole


class InvitationCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    email: EmailStr
    role: OrganizationRole

    @field_validator("email")
    @classmethod
    def normalize_email(
        cls,
        email: EmailStr,
    ) -> str:
        return str(email).lower()


class InvitationAcceptRequest(BaseModel):
    token: str = Field(
        min_length=32,
        max_length=256,
    )


class InvitationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    organization_id: UUID
    email: EmailStr
    role: OrganizationRole
    invited_by_user_id: UUID | None
    expires_at: datetime
    accepted_at: datetime | None
    created_at: datetime


class InvitationCreatedResponse(InvitationResponse):
    token: str
