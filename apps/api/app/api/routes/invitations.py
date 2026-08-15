from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import (
    CurrentUser,
    DatabaseSession,
    OrganizationAdminMembership,
)
from app.core.config import settings
from app.core.security import (
    generate_invitation_token,
    hash_invitation_token,
)
from app.crud.invitation import (
    create_invitation,
    get_active_invitation_by_token_hash,
    get_pending_invitation_by_email,
    list_pending_invitations,
    mark_invitation_accepted,
)
from app.crud.membership import (
    create_membership,
    get_membership,
)
from app.crud.user import get_user_by_email
from app.models.membership import OrganizationRole
from app.schemas.invitation import (
    InvitationAcceptRequest,
    InvitationCreate,
    InvitationCreatedResponse,
    InvitationResponse,
)
from app.schemas.membership import (
    MembershipCreate,
    MembershipResponse,
)

router = APIRouter(
    tags=["organization invitations"],
)


@router.post(
    "/organizations/{organization_id}/invitations",
    response_model=InvitationCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an organization invitation",
)
def create_invitation_endpoint(
    organization_id: UUID,
    invitation_data: InvitationCreate,
    admin_membership: OrganizationAdminMembership,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> InvitationCreatedResponse:
    email = str(invitation_data.email)

    existing_user = get_user_by_email(
        db,
        email,
    )

    if existing_user is not None:
        existing_membership = get_membership(
            db,
            organization_id,
            existing_user.id,
        )

        if existing_membership is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=("User is already a member of this organization."),
            )

    existing_invitation = get_pending_invitation_by_email(
        db,
        organization_id,
        email,
    )

    if existing_invitation is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("A pending invitation already exists for this email."),
        )

    raw_token = generate_invitation_token()

    expires_at = datetime.now(UTC) + timedelta(days=settings.invitation_ttl_days)

    try:
        invitation = create_invitation(
            db=db,
            organization_id=organization_id,
            invited_by_user_id=current_user.id,
            invitation_data=invitation_data,
            token_hash=hash_invitation_token(raw_token),
            expires_at=expires_at,
        )

        db.commit()
        db.refresh(invitation)

    except IntegrityError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create invitation.",
        ) from error

    response_data = InvitationResponse.model_validate(invitation).model_dump()

    return InvitationCreatedResponse(
        **response_data,
        token=raw_token,
    )


@router.get(
    "/organizations/{organization_id}/invitations",
    response_model=list[InvitationResponse],
    summary="List pending organization invitations",
)
def list_invitations_endpoint(
    organization_id: UUID,
    _admin: OrganizationAdminMembership,
    db: DatabaseSession,
) -> list[InvitationResponse]:
    invitations = list_pending_invitations(
        db,
        organization_id,
    )

    return [InvitationResponse.model_validate(invitation) for invitation in invitations]


@router.post(
    "/invitations/accept",
    response_model=MembershipResponse,
    summary="Accept an organization invitation",
)
def accept_invitation_endpoint(
    invitation_data: InvitationAcceptRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> MembershipResponse:
    invitation = get_active_invitation_by_token_hash(
        db,
        hash_invitation_token(invitation_data.token),
    )

    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or expired.",
        )

    if invitation.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=("Invitation belongs to a different account."),
        )

    existing_membership = get_membership(
        db,
        invitation.organization_id,
        current_user.id,
    )

    if existing_membership is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("User is already a member of this organization."),
        )

    try:
        membership = create_membership(
            db,
            invitation.organization_id,
            MembershipCreate(
                user_id=current_user.id,
                role=OrganizationRole(invitation.role),
            ),
        )

        mark_invitation_accepted(
            db,
            invitation,
        )

        db.commit()
        db.refresh(membership)

    except IntegrityError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to accept invitation.",
        ) from error

    return MembershipResponse.model_validate(membership)
