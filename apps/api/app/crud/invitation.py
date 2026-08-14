from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.invitation import (
    OrganizationInvitation,
)
from app.schemas.invitation import InvitationCreate


def create_invitation(
    db: Session,
    organization_id: UUID,
    invited_by_user_id: UUID,
    invitation_data: InvitationCreate,
    token_hash: str,
    expires_at: datetime,
) -> OrganizationInvitation:
    invitation = OrganizationInvitation(
        organization_id=organization_id,
        email=str(invitation_data.email),
        role=invitation_data.role.value,
        token_hash=token_hash,
        invited_by_user_id=invited_by_user_id,
        expires_at=expires_at,
    )

    db.add(invitation)
    db.flush()

    return invitation


def get_pending_invitation_by_email(
    db: Session,
    organization_id: UUID,
    email: str,
) -> OrganizationInvitation | None:
    statement = select(
        OrganizationInvitation
    ).where(
        OrganizationInvitation.organization_id
        == organization_id,
        OrganizationInvitation.email == email,
        OrganizationInvitation.accepted_at.is_(None),
        OrganizationInvitation.expires_at > func.now(),
    )

    return db.scalar(statement)


def get_active_invitation_by_token_hash(
    db: Session,
    token_hash: str,
) -> OrganizationInvitation | None:
    statement = select(
        OrganizationInvitation
    ).where(
        OrganizationInvitation.token_hash
        == token_hash,
        OrganizationInvitation.accepted_at.is_(None),
        OrganizationInvitation.expires_at > func.now(),
    )

    return db.scalar(statement)


def list_pending_invitations(
    db: Session,
    organization_id: UUID,
) -> list[OrganizationInvitation]:
    statement = (
        select(OrganizationInvitation)
        .where(
            OrganizationInvitation.organization_id
            == organization_id,
            OrganizationInvitation.accepted_at.is_(
                None
            ),
            OrganizationInvitation.expires_at
            > func.now(),
        )
        .order_by(
            OrganizationInvitation.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


def mark_invitation_accepted(
    db: Session,
    invitation: OrganizationInvitation,
) -> None:
    invitation.accepted_at = datetime.now(UTC)
    db.flush()