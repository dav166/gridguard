from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.membership import (
    OrganizationMembership,
)
from app.schemas.membership import MembershipCreate


def create_membership(
    db: Session,
    organization_id: UUID,
    membership_data: MembershipCreate,
) -> OrganizationMembership:
    membership = OrganizationMembership(
        organization_id=organization_id,
        user_id=membership_data.user_id,
        role=membership_data.role.value,
    )

    db.add(membership)
    db.flush()

    return membership


def get_membership(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
) -> OrganizationMembership | None:
    statement = select(OrganizationMembership).where(
        OrganizationMembership.organization_id == organization_id,
        OrganizationMembership.user_id == user_id,
    )

    return db.scalar(statement)


def list_organization_memberships(
    db: Session,
    organization_id: UUID,
) -> list[OrganizationMembership]:
    statement = (
        select(OrganizationMembership)
        .where(OrganizationMembership.organization_id == organization_id)
        .order_by(OrganizationMembership.created_at)
    )

    return list(db.scalars(statement).all())
