from typing import Literal

from pydantic import BaseModel

ApplicationStatus = Literal["ok", "degraded"]
DatabaseStatus = Literal["connected", "unavailable"]


class HealthResponse(BaseModel):
    status: ApplicationStatus
    service: str
    environment: str
    version: str
    database: DatabaseStatus