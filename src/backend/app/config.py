from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # Default: migrated RECRUIT DB on the legacy snapshot Postgres (host port 15432).
    # Docker Compose backend instead uses DATABASE_URL=...@postgres:5432/... (internal volume).
    database_url: str = "postgresql://postgres:postgres@localhost:15432/recruit_db"
    
    # Security (default must match docker-compose.yml / docker-compose.prod.yml so host
    # uvicorn and containerized backend issue interchangeable JWTs in dev).
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()


