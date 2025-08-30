import subprocess

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import text

from settings.config import dbsettings
from settings.loguru_config import logger


class DBConnection:
    """
    Класс для управления подключением к PostgreSQL через SQLAlchemy.
    """

    def __init__(self):
        """
        Инициализирует подключение, создавая асинхронный движок SQLAlchemy.
        """
        self.settings = dbsettings
        self.engine = self.init_async_engine()

    def init_async_engine(self) -> AsyncEngine:
        """
        Создать асинхронный движок SQLAlchemy для работы с PostgreSQL.

        Использует драйвер `asyncpg`.

        :return: Экземпляр `AsyncEngine`.
        """
        return create_async_engine(self.settings.asyncpg_url, echo=False)

    def init_engine(self) -> Engine:
        """
        Создать синхронный движок SQLAlchemy для работы с PostgreSQL.

        Использует драйвер `psycopg2`.

        :return: Экземпляр `Engine`.
        """
        return create_engine(
            self.settings.psycopg2_uri,
            isolation_level="AUTOCOMMIT",
            echo=False,
        )

    def async_session_maker(self) -> async_sessionmaker[AsyncSession]:
        """
        Создать фабрику асинхронных сессий для работы с БД.

        :return: Экземпляр `async_sessionmaker`.
        """
        return sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    def create_database(self) -> None:
        """
        Создать базу данных, если она ещё не существует.

        - Проверяет, что PostgreSQL запущен (`pg_isready`).
        - Подключается к системной БД `postgres`.
        - Выполняет SQL-запрос для проверки существования базы.
        - Если базы нет — создаёт её.

        :raises Exception: Логирует ошибку, если создание БД не удалось.
        """
        try:
            subprocess.run(["pg_isready"], check=True)
        except subprocess.CalledProcessError:
            logger.error("PostgreSQL is not running")
            return

        engine = create_engine(
            f"postgresql://{self.settings.DB_USER}:{self.settings.DB_PASSWORD}"
            f"@{self.settings.DB_HOST}:{self.settings.DB_PORT}/postgres",
            isolation_level="AUTOCOMMIT",
        )
        db_name = self.settings.DB_NAME
        with engine.connect() as connection:
            try:
                result = connection.execute(
                    text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
                )
                exists = result.scalar() is not None
                if not exists:
                    connection.execute(text(f"CREATE DATABASE {db_name}"))
                    logger.info(f"Database {db_name} created")
                else:
                    logger.info(f"Database {db_name} already exists.")
            except Exception as e:
                logger.error(f"Error while creating database: {e}")
            finally:
                connection.close()


conn = DBConnection()
async_session_maker = conn.async_session_maker()
