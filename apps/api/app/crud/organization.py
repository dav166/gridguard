from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.membership import OrganizationMembership
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate


def create_organization(
    db: Session,
    organization_data: OrganizationCreate,
) -> Organization:
    organization = Organization(
        name=organization_data.name,
        slug=organization_data.slug,
    )

    db.add(organization)
    db.flush()

    return organization


def get_organization(
    db: Session,
    organization_id: UUID,
) -> Organization | None:
    return db.get(
        Organization,
        organization_id,
    )


def get_organization_by_slug(
    db: Session,
    slug: str,
) -> Organization | None:
    statement = select(Organization).where(Organization.slug == slug)

    return db.scalar(statement)


def list_user_organizations(
    db: Session,
    user_id: UUID,
) -> list[Organization]:
    statement = (
        select(Organization)
        .join(
            OrganizationMembership,
            OrganizationMembership.organization_id == Organization.id,
        )
        .where(OrganizationMembership.user_id == user_id)
        .order_by(Organization.created_at.desc())
    )

    return list(db.scalars(statement).all())
