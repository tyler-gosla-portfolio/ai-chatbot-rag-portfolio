from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot_rag"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/chatbot_rag"

    # For testing with SQLite
    TESTING: bool = False
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    OPENAI_API_KEY: str = "sk-test"

    JWT_SECRET: str = "dev-secret-key-change-in-production-minimum-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 10
    MAX_DOCUMENTS_PER_USER: int = 50

    CHUNK_SIZE_TOKENS: int = 500
    CHUNK_OVERLAP_TOKENS: int = 50
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    COMPLETION_MODEL: str = "gpt-4o"
    SIMILARITY_THRESHOLD: float = 0.72
    TOP_K: int = 5

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    LOG_LEVEL: str = "info"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
