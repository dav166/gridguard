from datetime import UTC, datetime, timedelta

from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Response,
    status,
)
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import (
    CurrentUser,
    DatabaseSession,
)
from app.core.config import settings
from app.core.security import (
    generate_session_token,
    hash_session_token,
    verify_password,
)
from app.crud.user import (
    create_user,
    get_user_by_email,
)
from app.crud.user_session import (
    create_user_session,
    delete_user_session_by_token_hash,
)
from app.schemas.auth import LoginRequest
from app.schemas.user import (
    UserCreate,
    UserResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


def issue_session(
    response: Response,
    db: DatabaseSession,
    user_id,
) -> None:
    raw_token = generate_session_token()

    expires_at = datetime.now(UTC) + timedelta(days=settings.session_ttl_days)

    create_user_session(
        db=db,
        user_id=user_id,
        token_hash=hash_session_token(raw_token),
        expires_at=expires_at,
    )

    response.set_cookie(
        key=settings.session_cookie_name,
        value=raw_token,
        max_age=(settings.session_ttl_days * 24 * 60 * 60),
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserCreate,
    response: Response,
    db: DatabaseSession,
) -> UserResponse:
    existing_user = get_user_by_email(
        db,
        str(user_data.email),
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    try:
        user = create_user(
            db,
            user_data,
        )
    except IntegrityError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from error

    issue_session(
        response,
        db,
        user.id,
    )

    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=UserResponse,
)
def login(
    login_data: LoginRequest,
    response: Response,
    db: DatabaseSession,
) -> UserResponse:
    user = get_user_by_email(
        db,
        str(login_data.email),
    )

    if user is None or not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    issue_session(
        response,
        db,
        user.id,
    )

    return UserResponse.model_validate(user)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    request: Request,
    db: DatabaseSession,
) -> Response:
    session_token = request.cookies.get(settings.session_cookie_name)

    if session_token is not None:
        delete_user_session_by_token_hash(
            db,
            hash_session_token(session_token),
        )

    response = Response(status_code=status.HTTP_204_NO_CONTENT)

    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )

    return response


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: CurrentUser,
) -> UserResponse:
    return UserResponse.model_validate(current_user)
