from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/rag_ingestion"
    celery_broker_url: str = "amqp://guest:guest@localhost:5672//"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "rag_chunks"
    chunk_size: int = 800
    chunk_overlap: int = 120


settings = Settings()
