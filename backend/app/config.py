from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # database
    DATABASE_URL: PostgresDsn

    # cors
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]

    # ml model
    MODEL_PATH: str = "models/modelo_aluguel.pkl"

    # app
    STAGE: str = "development"
    DEBUG: bool = False

    @field_validator("STAGE")
    @classmethod
    def validate_stage(cls, v: str) -> str:
        allowed = {"development", "production", "test"}
        if v not in allowed:
            raise ValueError(f"STAGE must be one of {allowed}")
        return v


settings = Settings()
