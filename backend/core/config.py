import os
from dataclasses import dataclass


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/resumematch_ai",
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    db_min_connections: int = int(os.getenv("DB_MIN_CONNECTIONS", "5"))
    db_max_connections: int = int(os.getenv("DB_MAX_CONNECTIONS", "20"))
    secret_key: str = os.getenv("SECRET_KEY", "")
    allowed_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    )
    access_token_minutes: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "30"))
    refresh_token_days: int = int(os.getenv("REFRESH_TOKEN_DAYS", "14"))
    secure_cookies: bool = _as_bool(os.getenv("SECURE_COOKIES"))
    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
    max_pdf_pages: int = int(os.getenv("MAX_PDF_PAGES", "25"))
    max_image_pixels: int = int(os.getenv("MAX_IMAGE_PIXELS", "25000000"))
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    email_verification_required: bool = _as_bool(
        os.getenv("EMAIL_VERIFICATION_REQUIRED")
    )
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from: str = os.getenv("SMTP_FROM", "noreply@resumematch.local")
    smtp_starttls: bool = _as_bool(os.getenv("SMTP_STARTTLS"), default=True)

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    def validate(self) -> None:
        if self.db_min_connections < 1:
            raise RuntimeError("DB_MIN_CONNECTIONS must be at least 1.")
        if self.db_max_connections < self.db_min_connections:
            raise RuntimeError(
                "DB_MAX_CONNECTIONS must be greater than or equal to DB_MIN_CONNECTIONS."
            )
        if self.is_production and len(self.secret_key) < 32:
            raise RuntimeError(
                "SECRET_KEY must be configured with at least 32 characters in production."
            )
        if self.is_production and not self.secure_cookies:
            raise RuntimeError("SECURE_COOKIES must be enabled in production.")
        if self.is_production and (
            not self.allowed_origins
            or "*" in self.allowed_origins
            or any(not origin.startswith("https://") for origin in self.allowed_origins)
        ):
            raise RuntimeError(
                "ALLOWED_ORIGINS must contain explicit HTTPS origins in production."
            )
        if self.is_production and not self.frontend_url.startswith("https://"):
            raise RuntimeError("FRONTEND_URL must use HTTPS in production.")
        if (
            self.is_production
            and self.email_verification_required
            and not self.smtp_host
        ):
            raise RuntimeError(
                "SMTP_HOST is required when email verification is enabled."
            )


settings = Settings()
