from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://venture:venture_secret@postgres:5432/venture_copilot"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # AI
    AI_PROVIDER: str = "mock"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    EXA_API_KEY: str = ""

    # Auth placeholder
    DEFAULT_USER_ID: str = "demo_user"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
