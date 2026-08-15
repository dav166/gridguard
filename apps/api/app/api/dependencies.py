from typing import Annotated
from uuid import UUID

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_session_token
from app.crud.membership import get_membership
from app.crud.user import get_user
from app.crud.user_session import (
    get_active_user_session,
)
from app.db.session import get_db
from app.models.membership import (
    OrganizationMembership,
    OrganizationRole,
)
from app.models.user import User

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


def get_current_user(
    request: Request,
    db: DatabaseSession,
) -> User:
    session_token = request.cookies.get(settings.session_cookie_name)

    if session_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    user_session = get_active_user_session(
        db,
        hash_session_token(session_token),
    )

    if user_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session.",
        )

    user = get_user(
        db,
        user_session.user_id,
    )

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive account.",
        )

    return user


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]


def get_current_organization_membership(
    organization_id: UUID,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> OrganizationMembership:
    membership = get_membership(
        db,
        organization_id,
        current_user.id,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    return membership


CurrentOrganizationMembership = Annotated[
    OrganizationMembership,
    Depends(get_current_organization_membership),
]


def require_organization_admin(
    membership: CurrentOrganizationMembership,
) -> OrganizationMembership:
    if membership.role != OrganizationRole.ORGANIZATION_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=("Organization administrator permission required."),
        )

    return membership


OrganizationAdminMembership = Annotated[
    OrganizationMembership,
    Depends(require_organization_admin),
]


PROJECT_WRITE_ROLES = {
    OrganizationRole.ORGANIZATION_ADMIN.value,
    OrganizationRole.SAFETY_MANAGER.value,
    OrganizationRole.SUPERVISOR.value,
}


def require_project_write_access(
    membership: CurrentOrganizationMembership,
) -> OrganizationMembership:
    if membership.role not in PROJECT_WRITE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=("Project management permission required."),
        )

    return membership


ProjectWriteMembership = Annotated[
    OrganizationMembership,
    Depends(require_project_write_access),
]
