import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Industrial Knowledge Intelligence Platform"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # JWT
    JWT_SECRET: str = "change_this_to_a_random_secret_key_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 1440

    # Database
    SQLITE_DB: str = "database/knowledge_platform.db"

    # ChromaDB
    CHROMA_DB_PATH: str = "vector_db/"

    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # Groq AI
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Embedding
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    # Upload
    UPLOAD_DIR: str = "uploads/"
    MAX_UPLOAD_SIZE_MB: int = 50

    # Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def DATABASE_URL(self) -> str:
        return f"sqlite+aiosqlite:///{self.SQLITE_DB}"

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f"sqlite:///{self.SQLITE_DB}"

    @property
    def MAX_UPLOAD_SIZE_BYTES(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


BASE_DIR = Path(__file__).resolve().parent.parent.parent
