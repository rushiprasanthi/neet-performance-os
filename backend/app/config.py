"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "NEET API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # Database
    database_url: str = "postgresql+asyncpg://neet_user:Bhavanarushi@localhost:5432/neet_pos"
    database_echo: bool = False
    database_pool_size: int = Field(default=20, description="Base DB connection pool size")
    database_max_overflow: int = Field(default=10, description="Maximum overflow DB connections")

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT Secret Key. MUST be overridden in production!"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # CORS
    frontend_url: str = "http://localhost:5173"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period_seconds: int = 60

    # API Documentation
    openapi_url: str = "/openapi.json"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"

    @model_validator(mode='after')
    def validate_production_secrets(self) -> 'Settings':
        if self.environment == "production" and self.secret_key == "your-secret-key-change-in-production":
            raise ValueError("CRITICAL: Default secret_key is active in production environment!")
        return self

    # Pydantic V2 Configuration syntax
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore unknown env vars to prevent injection/crashes
    )


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


settings = get_settings()