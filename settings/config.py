from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Загружаем переменные окружения из .env
load_dotenv()


class DBSettings(BaseSettings):
    """
    Настройки подключения к базе данных PostgreSQL.

    Загружаются из `.env`.
    """

    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: int
    DB_HOST: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def psycopg2_uri(self) -> str:
        """
        URI для подключения через `psycopg2` (синхронный драйвер).

        :return: Строка подключения формата `postgresql+psycopg://...`
        """
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def asyncpg_url(self) -> str:
        """
        URI для подключения через `asyncpg` (асинхронный драйвер).

        :return: Строка подключения формата `postgresql+asyncpg://...`
        """
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def psql_url(self) -> str:
        """
        URI для использования утилитой psql (без указания драйвера).

        :return: Строка подключения формата `postgresql://...`
        """
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


class JWTSettings(BaseSettings):
    """
    Настройки для JWT-аутентификации.

    Загружаются из `.env.jwt`.
    """

    JWT_SECRET: str
    JWT_ALG: str
    ACCESS_TOKEN_EXPIRE_MIN: int

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env.jwt",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

app_middleware = {'allow_origins': origins,
                  'allow_credentials': True,
                  'allow_methods': ["*"],
                  'allow_headers': ["*"],
                  }

dbsettings = DBSettings()
jwtsettings = JWTSettings()
