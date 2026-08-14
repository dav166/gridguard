from typing import Annotated

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_session_token
from app.crud.user import get_user
from app.crud.user_session import (
    get_active_user_session,
)
from app.db.session import get_db
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
