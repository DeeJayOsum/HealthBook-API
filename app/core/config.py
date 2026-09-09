from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Healthcare Appointment Booking API"
    environment: str = "development"
    database_url: str = (
        "postgresql+asyncpg://healthcare:healthcare@localhost:5432/healthcare"
    )
    jwt_secret_key: str = "change-me-in-development"
    access_token_expire_minutes: int = 30
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def validate_production_secret(self) -> "Settings":
        if self.environment != "development" and (
            self.jwt_secret_key == "change-me-in-development"
            or len(self.jwt_secret_key) < 32
        ):
            raise ValueError(
                "JWT_SECRET_KEY must be at least 32 characters outside development"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()