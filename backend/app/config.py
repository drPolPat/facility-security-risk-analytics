"""Application settings, loaded from environment / the repo-root .env file."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo root is one level above backend/; the shared .env lives there.
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    app_name: str = "facility-security-risk-analytics"

    # CORS uses TWO independent variables -- keep them straight:
    #   CORS_ORIGINS       comma-separated list of *exact* origins (allow_origins)
    #   CORS_ORIGIN_REGEX  a single regex, e.g. https://.*\.vercel\.app
    #                      (allow_origin_regex) -- use this for Vercel previews.
    # A regex placed in CORS_ORIGINS is treated as one literal origin and never
    # matches.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    cors_origin_regex: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Module-level handle for the common case; tests can call get_settings() fresh.
settings = get_settings()
