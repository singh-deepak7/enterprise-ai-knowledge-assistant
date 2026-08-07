from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Set


class Settings(BaseSettings):
    APP_NAME: str = "Enterprise AI Knowledge System"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    OPENAI_API_KEY: str

    CHAT_MODEL: str = "gpt-5"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    CHROMA_DB_DIR: str = "app/chroma_db"
    CHROMA_COLLECTION: str = "enterprise_knowledge"

    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    EMBEDDING_BATCH_SIZE: int = 100

    TOP_K_RESULTS: int = 5
    SIMILARITY_SCORE_THRESHOLD: float = 0.20

    AI_DEBUG: bool = False

    UPLOAD_DIR: str = "app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 25

    ALLOWED_EXTENSIONS: set[str] = {
    ".pdf",
    ".txt",
    ".csv",
    ".xlsx",
    }

    ALLOWED_CONTENT_TYPES: set[str] = {
        "application/pdf",
        "text/plain",
        "text/csv",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }

    LOG_LEVEL: str = "INFO"

    DOCUMENT_DB_PATH: str = "app/data/documents.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

