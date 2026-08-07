from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API and database health",
)
def health_check(
    response: Response,
    db: Session = Depends(get_db),
) -> HealthResponse:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return HealthResponse(
            status="degraded",
            service=settings.app_name,
            environment=settings.environment,
            version=settings.app_version,
            database="unavailable",
        )

    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.environment,
        version=settings.app_version,
        database="connected",
    )