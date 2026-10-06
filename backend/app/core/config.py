from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    environment: str
    database_url: str
    cors_origins: str
    python_executable: str
    max_execution_time: float
    max_output_size: int
    chat_history_turns: int
    google_api_key: str
    google_model: str
    google_temperature: float

    @field_validator("python_executable", mode="after")
    @classmethod
    def resolve_python_executable(cls, value: str) -> str:
        executable = Path(value).expanduser()
        if executable.is_absolute():
            return str(executable)
        backend_root = Path(__file__).resolve().parents[2]
        return str((backend_root / executable).resolve())

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
