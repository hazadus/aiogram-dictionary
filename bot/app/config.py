from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    SENTRY_DSN: str | None = Field(default=None)
    OPENAI_API_KEY: str
    ALLOWED_USERS: list[str]


settings = Settings()
