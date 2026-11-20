from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Read from environment variables (or a local .env file), e.g. DATABASE_URL."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://library:library@localhost:5432/library"
    test_database_url: str = "postgresql+psycopg://library:library@localhost:5432/library_test"


@lru_cache
def get_settings() -> Settings:
    return Settings()
