from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://kaaj:kaaj@localhost:5432/kaaj"

    # Hatchet
    HATCHET_CLIENT_TOKEN: str = ""

    # Anthropic
    ANTHROPIC_API_KEY: str = ""

    # App
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"


settings = Settings()
