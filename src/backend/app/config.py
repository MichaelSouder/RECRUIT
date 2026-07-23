from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional, List


class Settings(BaseSettings):
    # Default: migrated RECRUIT DB on the legacy snapshot Postgres (host port 15432).
    # Docker Compose backend instead uses DATABASE_URL=...@postgres:5432/... (internal volume).
    database_url: str = "postgresql://postgres:postgres@localhost:15432/recruit_db"

    # Security — required, no default. Every deploy path (docker-compose*.yml,
    # scripts/start-stack-manual.sh, scripts/airgap/stack.py) must set SECRET_KEY;
    # the app now refuses to start without one, rather than silently issuing JWTs
    # signed with a value anyone can read in this repo.
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be set and at least 32 characters long")
        return v

    # Encrypts Subject.ssn at rest (see app/core/encryption.py). Required, no default,
    # same reasoning as secret_key: a comment on the column isn't a mitigation. Losing this
    # value after data has been written makes every stored SSN permanently unrecoverable —
    # back it up like any other production secret, separately from SECRET_KEY.
    ssn_encryption_key: str

    @field_validator("ssn_encryption_key")
    @classmethod
    def validate_ssn_encryption_key(cls, v: str) -> str:
        if not v or len(v) < 32:
            raise ValueError("SSN_ENCRYPTION_KEY must be set and at least 32 characters long")
        return v

    # Redis — auth is required in every deployed environment (see docs/BACKEND_REVIEW.md
    # §8); the URL must carry credentials, e.g. redis://:password@host:6379/0
    redis_url: str = "redis://:password@localhost:6379/0"
    
    # CORS
    cors_origins: str = (
        "http://localhost:5173,http://localhost:5174,http://localhost:3000,"
        "http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:18080"
    )
    
    # Application
    debug: bool = True
    environment: str = "development"

    # First boot (e.g. docker-compose.prod): create a single admin if users table is empty
    seed_initial_admin: bool = False
    initial_admin_email: str = "admin@example.com"
    initial_admin_password: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()


