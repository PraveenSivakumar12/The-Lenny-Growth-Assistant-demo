"""
Application configuration.
Resolve repository data and .env consistently whether launched from the repo root,
backend/ or the production container. Environment variables override these defaults.
"""
from pathlib import Path
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# In a source checkout this is <repo>/backend; in the combined container it is /app.
PACKAGE_ROOT = Path(__file__).resolve().parents[2]
if (PACKAGE_ROOT / "data").is_dir() or not (PACKAGE_ROOT.parent / "data").is_dir():
    PROJECT_ROOT = PACKAGE_ROOT
else:
    PROJECT_ROOT = PACKAGE_ROOT.parent
DATA_ROOT = PROJECT_ROOT / "data"
ENV_FILE = PROJECT_ROOT / ".env"


def _resolve_repo_path(value: str) -> str:
    path = Path(value).expanduser()
    if path.is_absolute():
        return str(path.resolve())
    cwd_candidate = (Path.cwd() / path).resolve()
    if cwd_candidate.exists():
        return str(cwd_candidate)
    return str((PROJECT_ROOT / path).resolve())


def _resolve_sqlite_url(value: Optional[str]) -> Optional[str]:
    if not value or not value.startswith("sqlite") or ":memory:" in value:
        return value
    marker = ":///"
    if marker not in value:
        return value
    scheme, path_part = value.split(marker, 1)
    path = Path(path_part).expanduser()
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()
    # Three slashes plus an absolute POSIX path yields sqlite:////absolute/path;
    # Windows paths remain sqlite:///C:/path, which SQLAlchemy understands.
    return f"{scheme}{marker}{path.as_posix()}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "The Lenny Growth Assistant"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    DATABASE_URL: str = f"sqlite+aiosqlite:///{(DATA_ROOT / 'lenny_growth.db').as_posix()}"
    SYNC_DATABASE_URL: Optional[str] = None

    DEFAULT_LLM_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    TRANSCRIPTS_DATA_DIR: str = str(DATA_ROOT / "transcripts")
    VECTOR_INDEX_DIR: str = str(DATA_ROOT / "index")
    TOP_K_RETRIEVAL: int = 4
    SIMILARITY_THRESHOLD: float = 0.35

    CORS_ORIGINS: List[str] = Field(default_factory=lambda: [
        "http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"
    ])

    @field_validator("TRANSCRIPTS_DATA_DIR", "VECTOR_INDEX_DIR", mode="after")
    @classmethod
    def resolve_data_directories(cls, value: str) -> str:
        return _resolve_repo_path(value)

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def resolve_database_path(cls, value: str) -> str:
        return _resolve_sqlite_url(value) or value

    @field_validator("SYNC_DATABASE_URL", mode="after")
    @classmethod
    def resolve_sync_database_path(cls, value: Optional[str]) -> Optional[str]:
        return _resolve_sqlite_url(value)


settings = Settings()
