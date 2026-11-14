from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSetting, SettingConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSetting):

    model_config = SettingConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True
    )

    app_name: str = "BizPilot AI"
    app_env: Literal["development", "testing", "production"] = "development"
    debug: bool = True
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    api_host: str = "127.0.0.1"
    api_port: int = 8000

    google_api_key: SecretStr | None = None
    gemini_model = "gemiini-3.5-flash-lite"

    database_path: Path = (
        PROJECT_ROOT / "storage" / "database" / "bizpilot.db"
    )

    chroma_persist_directory: Path = (
        PROJECT_ROOT / "storage" / "chroma"
    )

    embedding_model: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    langsmith_api_key: SecretStr | None = None
    langsmith_tracing: bool = False
    langsmith_project: str = "bizpilot-ai"
    langsmith_endpoint: str = "https://api.smith.langchain.com"

    max_upload_size_mb: int = 20


settings = Settings()