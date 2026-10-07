from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_secret: str = "local-development-secret-change-me"
    database_url: str = "sqlite:///./payments.db"
    frontend_origin: str = "http://localhost:5173"
    access_token_minutes: int = 480

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

