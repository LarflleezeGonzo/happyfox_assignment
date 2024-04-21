from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    DBI_URI: str = "sqlite:///emails.db"
    EMAIL_MAX_MESSAGES: int = 20

settings = Settings()