from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.user_session import UserSession


def create_user_session(
    db: Session,
    user_id: UUID,
    token_hash: str,
    expires_at: datetime,
) -> UserSession:
    user_session = UserSession(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    db.add(user_session)
    db.commit()
    db.refresh(user_session)

    return user_session


def get_active_user_session(
    db: Session,
    token_hash: str,
) -> UserSession | None:
    statement = select(UserSession).where(
        UserSession.token_hash == token_hash,
        UserSession.expires_at > func.now(),
    )

    return db.scalar(statement)


def delete_user_session_by_token_hash(
    db: Session,
    token_hash: str,
) -> None:
    statement = delete(UserSession).where(UserSession.token_hash == token_hash)

    db.execute(statement)
    db.commit()
