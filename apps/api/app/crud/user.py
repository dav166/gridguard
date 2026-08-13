from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


def create_user(
    db: Session,
    user_data: UserCreate,
) -> User:
    user = User(
        email=str(user_data.email),
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user(
    db: Session,
    user_id: UUID,
) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    normalized_email = email.strip().lower()

    statement = select(User).where(User.email == normalized_email)

    return db.scalar(statement)
