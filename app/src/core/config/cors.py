"""CORS configuration for production and development."""

from src.core.config.settings import get_settings


def get_cors_config() -> dict:
    """Get CORS configuration based on environment."""
    settings = get_settings()

    if settings.is_production:
        return {
            "allow_origins": [
                "https://yourdomain.com",
                "https://app.yourdomain.com",
            ],
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["*"],
            "max_age": 3600,
        }

    return {
        "allow_origins": settings.CORS_ORIGINS,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
        "max_age": 86400,
    }
