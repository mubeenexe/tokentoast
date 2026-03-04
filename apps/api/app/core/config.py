from pathlib import Path

from pydantic_settings import BaseSettings

# Load .env from the api app root (apps/api) so it works when run from monorepo root
_API_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _API_ROOT / ".env"


class Settings(BaseSettings):
    # App
    APP_NAME: str = "TokenToast API"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | staging | production

    # Database
    # Default points to local Postgres from docker-compose.
    # Override via env DATABASE_URL in other environments.
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5430/auth_db"

    # JWT
    # Use a non-empty default so development works even without .env.
    # In production, always override via JWT_SECRET_KEY env var.
    JWT_SECRET_KEY: str = "dev-change-me-in-production-min-32-bytes"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Cookies
    COOKIE_SECURE: bool = False  # True in production (HTTPS)
    COOKIE_SAMESITE: str = "Lax"  # "Strict" for more secure

    # Redis (rate limit + optional session/revocation cache)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Frontend origin for CORS (Next.js dev default)
    FRONTEND_ORIGIN: str = "http://localhost:3000"

    # Email verification and password reset tokens
    VERIFY_EMAIL_EXPIRE_MINUTES: int = 60
    RESET_PASSWORD_EXPIRE_MINUTES: int = 30

    # Rate limiting
    RATE_LIMIT_LOGIN_PER_MINUTE: int = 5
    RATE_LIMIT_REGISTER_PER_MINUTE: int = 3
    RATE_LIMIT_FORGOT_PASSWORD_PER_MINUTE: int = 3

    # SMTP – leave SMTP_HOST empty to disable real email (links logged in dev)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@example.com"
    SMTP_FROM_NAME: str = "TokenToast"
    SMTP_USE_TLS: bool = True

    def model_post_init(self, __context) -> None:
        # Strip whitespace so .env values don't break SMTP (e.g. trailing newline)
        object.__setattr__(self, "SMTP_HOST", (self.SMTP_HOST or "").strip())
        object.__setattr__(self, "SMTP_USER", (self.SMTP_USER or "").strip())
        object.__setattr__(self, "SMTP_PASSWORD", (self.SMTP_PASSWORD or "").strip())

    @property
    def email_enabled(self) -> bool:
        return bool(self.SMTP_HOST.strip())

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    class Config:
        env_file = str(_ENV_FILE) if _ENV_FILE.exists() else ".env"
        extra = "ignore"


settings = Settings()
