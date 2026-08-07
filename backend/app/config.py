"""
Central config. Everything environment-specific lives here so nothing
else in the app has to know whether it's running against local SQLite
or Railway Postgres.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Defaults to a local SQLite file so the app runs with zero setup.
    # In Week 2, set DATABASE_URL to the Railway Postgres connection
    # string and nothing else in the codebase needs to change.
    database_url: str = "sqlite:///./bus.db"

    secret_key: str = "dev-only-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 day

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
