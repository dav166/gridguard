from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.membership import OrganizationRole


class MembershipCreate(BaseModel):
    user_id: UUID
    role: OrganizationRole


class MembershipResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    organization_id: UUID
    user_id: UUID
    role: OrganizationRole
    created_at: datetime
