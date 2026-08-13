from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import DatabaseSession
from app.crud.organization import (
    create_organization,
    get_organization,
    get_organization_by_slug,
    list_organizations,
)
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
)

router = APIRouter(
    prefix="/organizations",
    tags=["organizations"],
)


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an organization",
)
def create_organization_endpoint(
    organization_data: OrganizationCreate,
    db: DatabaseSession,
) -> OrganizationResponse:
    existing_organization = get_organization_by_slug(
        db,
        organization_data.slug,
    )

    if existing_organization is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An organization with this slug already exists.",
        )

    try:
        organization = create_organization(
            db,
            organization_data,
        )
    except IntegrityError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An organization with this slug already exists.",
        ) from error

    return OrganizationResponse.model_validate(organization)


@router.get(
    "",
    response_model=list[OrganizationResponse],
    summary="List organizations",
)
def list_organizations_endpoint(
    db: DatabaseSession,
) -> list[OrganizationResponse]:
    organizations = list_organizations(db)

    return [OrganizationResponse.model_validate(organization) for organization in organizations]


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
    summary="Get an organization",
)
def get_organization_endpoint(
    organization_id: UUID,
    db: DatabaseSession,
) -> OrganizationResponse:
    organization = get_organization(
        db,
        organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    return OrganizationResponse.model_validate(organization)
