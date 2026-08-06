from fastapi import APIRouter

from app.core.config import settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API health",
)
def health_check() -> HealthResponse:
    return HealthResponse(
        service=settings.app_name,
        environment=settings.environment,
        version=settings.app_version,
    )