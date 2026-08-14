from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "GridGuard API"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    session_cookie_name: str = "gridguard_session"
    session_ttl_days: int = 7
    cookie_secure: bool = False

    database_url: str = (
        "postgresql+psycopg://gridguard:gridguard_dev_password@localhost:5432/gridguard"
    )

    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="GRIDGUARD_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

invitation_ttl_days: int = 7