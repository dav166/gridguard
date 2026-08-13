from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class UserCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    email: EmailStr

    full_name: str = Field(
        min_length=2,
        max_length=120,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("email")
    @classmethod
    def normalize_email(
        cls,
        email: EmailStr,
    ) -> str:
        return str(email).lower()


class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
