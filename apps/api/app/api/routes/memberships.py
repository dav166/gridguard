from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import (
    CurrentOrganizationMembership,
    DatabaseSession,
    OrganizationAdminMembership,
)
from app.crud.membership import (
    create_membership,
    get_membership,
    list_organization_memberships,
)
from app.crud.user import get_user
from app.schemas.membership import (
    MembershipCreate,
    MembershipResponse,
)

router = APIRouter(
    prefix="/organizations/{organization_id}/members",
    tags=["organization memberships"],
)


@router.get(
    "",
    response_model=list[MembershipResponse],
    summary="List organization members",
)
def list_members_endpoint(
    organization_id: UUID,
    _membership: CurrentOrganizationMembership,
    db: DatabaseSession,
) -> list[MembershipResponse]:
    memberships = list_organization_memberships(
        db,
        organization_id,
    )

    return [MembershipResponse.model_validate(membership) for membership in memberships]


@router.post(
    "",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an organization member",
)
def add_member_endpoint(
    organization_id: UUID,
    membership_data: MembershipCreate,
    _admin: OrganizationAdminMembership,
    db: DatabaseSession,
) -> MembershipResponse:
    user = get_user(
        db,
        membership_data.user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    existing_membership = get_membership(
        db,
        organization_id,
        membership_data.user_id,
    )

    if existing_membership is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("User is already a member of this organization."),
        )

    try:
        membership = create_membership(
            db,
            organization_id,
            membership_data,
        )

        db.commit()
        db.refresh(membership)

    except IntegrityError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Unable to create organization membership."),
        ) from error

    return MembershipResponse.model_validate(membership)
