from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DATABASE: str = "postgres"
    DB_USER: str = "admin"
    DB_PORT: int = 5432
    DB_PASSWORD: str = "password"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
