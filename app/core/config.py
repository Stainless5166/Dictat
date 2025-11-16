"""
Application configuration using Pydantic Settings

Loads configuration from environment variables and .env file
Validates all settings at startup
"""

from typing import List, Optional
from pydantic import AnyHttpUrl, EmailStr, Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables

    TODO Phase 1:
    - Add validation for all critical settings
    - Add computed properties for derived settings
    - Implement settings for different environments (dev/staging/prod)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Dictat"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = True
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = Field(default=8000, ge=1, le=65535)
    RELOAD: bool = True

    # Security
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-min-32-chars!!!",
        min_length=32
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1)
    PASSWORD_HASH_ALGORITHM: str = Field(default="argon2", pattern="^(bcrypt|argon2)$")

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = Field(default=5432, ge=1, le=65535)
    DB_USER: str = "dictat_user"
    DB_PASSWORD: str = "changeme"
    DB_NAME: str = "dictat_db"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = Field(default=20, ge=1)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0)
    DB_POOL_TIMEOUT: int = Field(default=30, ge=1)
    DB_POOL_RECYCLE: int = Field(default=3600, ge=0)

    @property
    def DATABASE_URL(self) -> str:
        """
        Construct PostgreSQL database URL

        TODO: Handle SSL mode for production
        """
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535)
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = Field(default=0, ge=0, le=15)
    REDIS_CACHE_TTL: int = Field(default=3600, ge=1)

    @property
    def REDIS_URL(self) -> str:
        """Construct Redis URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # OPA (Open Policy Agent)
    OPA_URL: str = "http://localhost:8181"
    OPA_POLICY_PATH: str = "/v1/data/dictat/allow"
    OPA_TIMEOUT: int = Field(default=5, ge=1)

    # File Storage
    STORAGE_BASE_PATH: str = "/app/storage"
    AUDIO_STORAGE_PATH: str = "/app/storage/audio"
    MAX_UPLOAD_SIZE: int = Field(default=104857600, ge=1)  # 100MB
    ALLOWED_AUDIO_FORMATS: List[str] = ["mp3", "wav", "m4a", "ogg", "flac"]
    CHUNK_SIZE: int = Field(default=1048576, ge=1)  # 1MB

    @field_validator("ALLOWED_AUDIO_FORMATS", mode="before")
    @classmethod
    def parse_audio_formats(cls, v: str | List[str]) -> List[str]:
        """Parse audio formats from comma-separated string or list"""
        if isinstance(v, str):
            return [fmt.strip() for fmt in v.split(",")]
        return v

    # Email
    MAIL_USERNAME: Optional[EmailStr] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[EmailStr] = None
    MAIL_PORT: int = Field(default=587, ge=1, le=65535)
    MAIL_SERVER: Optional[str] = None
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    MAIL_USE_CREDENTIALS: bool = True

    # Background Tasks
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    TASK_QUEUE_NAME: str = "dictat_tasks"

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = Field(default=30, ge=1)
    WS_MESSAGE_QUEUE_SIZE: int = Field(default=100, ge=1)

    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = Field(default=9090, ge=1, le=65535)
    METRICS_NAMESPACE: str = "dictat"
    LOG_FORMAT: str = Field(default="json", pattern="^(json|text)$")
    LOG_FILE: str = "/app/logs/dictat.log"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "30 days"

    # UK GDPR Compliance
    DATA_RETENTION_DAYS: int = Field(default=2555, ge=1)  # 7 years
    AUDIT_LOG_RETENTION_DAYS: int = Field(default=3650, ge=1)  # 10 years
    ENABLE_ENCRYPTION_AT_REST: bool = True
    ENABLE_FIELD_LEVEL_ENCRYPTION: bool = True
    DPO_EMAIL: Optional[EmailStr] = None
    DPO_NAME: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1)
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, ge=1)

    # Security Headers
    HSTS_MAX_AGE: int = Field(default=31536000, ge=0)
    CSP_POLICY: str = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Testing
    TEST_DATABASE_URL: Optional[str] = None
    TEST_REDIS_URL: Optional[str] = None

    # Feature Flags
    FEATURE_WEBSOCKET_ENABLED: bool = True
    FEATURE_EMAIL_NOTIFICATIONS: bool = True
    FEATURE_BACKGROUND_TASKS: bool = True
    FEATURE_METRICS_ENABLED: bool = True


# Initialize settings singleton
settings = Settings()
