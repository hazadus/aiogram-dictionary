from typing import Any
from urllib.parse import quote

from pydantic import Field, PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    SENTRY_DSN: str | None = Field(default=None)
    OPENAI_API_KEY: str
    ALLOWED_USERS: list[str]

    # Настройки базы данных
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="password")
    POSTGRES_DB: str = Field(default="bottec_negroni")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    ASYNC_POSTGRES_URI: PostgresDsn | None = None

    @validator("ASYNC_POSTGRES_URI", pre=True)
    def assemble_async_dsn(
        cls,
        v: str | None,
        values: dict[str, Any],
    ) -> PostgresDsn | str:
        """
        Собирает DSN для асинхронного подключения к БД PostgreSQL
        из настроек окружения.
        """

        if isinstance(v, str):
            return v

        postgres_port = values.get("POSTGRES_PORT")
        if postgres_port is None:
            raise ValueError("POSTGRES_PORT не может быть None")

        # Экранируем все специальные символы через quote для URL
        password = quote(
            str(values.get("POSTGRES_PASSWORD", "")),
            safe="",
        )

        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=password,
            host=values.get("POSTGRES_HOST"),
            port=int(postgres_port),
            path=f"{values.get('POSTGRES_DB') or ''}",
        )


settings = Settings()
