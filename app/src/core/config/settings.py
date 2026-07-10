from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Finance AI Agent"
    ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite+aiosqlite:///./finance_ai.db"

    SECRET_KEY: str = "change-me-in-production"

    CLERK_SECRET_KEY: str | None = None
    CLERK_PUBLISHABLE_KEY: str | None = None
    CLERK_JWKS_URL: str | None = None

    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://claude.ai",
        "*",
    ]

    LOG_LEVEL: str = "INFO"

    N8N_WEBHOOK_SECRET: str | None = None

    # Zoho Books
    ZOHO_CLIENT_ID: str | None = None
    ZOHO_CLIENT_SECRET: str | None = None
    ZOHO_ACCESS_TOKEN: str | None = None
    ZOHO_REFRESH_TOKEN: str | None = None
    ZOHO_ORG_ID: str | None = None
    ZOHO_API_KEY: str | None = None

    # Meta Ads
    META_APP_ID: str | None = None
    META_APP_SECRET: str | None = None
    META_ACCESS_TOKEN: str | None = None
    META_AD_ACCOUNT_ID: str | None = None

    # Google Ads
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REFRESH_TOKEN: str | None = None
    GOOGLE_CUSTOMER_ID: str | None = None

    # Razorpay
    RAZORPAY_KEY_ID: str | None = None
    RAZORPAY_KEY_SECRET: str | None = None

    # Bank CSV
    BANK_STATEMENT_PATH: str = "./data/bank_statement.csv"
    BANK_ACCOUNT_NUMBER: str | None = None
    BANK_NAME: str = "HDFC"

    # Credit Card CSV
    CREDIT_CARD_STATEMENT_PATH: str = "./data/credit_card_statement.csv"
    CREDIT_CARD_LAST_4_DIGITS: str | None = None

    # Google Sheets (Demo/Presentation)
    GOOGLE_SHEETS_ID: str | None = None
    GOOGLE_SHEETS_OAUTH_TOKEN: str | None = None
    USE_SHEETS_FOR_DEMO: bool = True

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
