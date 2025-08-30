from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from database.models.base import Base
from database.models.models import Resume, User
from settings.engine import async_session_maker

TModel = TypeVar("TModel", bound=Base)


class BaseDAO(Generic[TModel]):
    """
    Базовый DAO для CRUD-операций с асинхронной SQLAlchemy-сессией.

    Атрибуты:
        model (Type[TModel]): SQLAlchemy-модель, с которой работает DAO.
        _session_factory (sessionmaker): Фабрика асинхронных сессий.
    """

    model: Type[TModel]
    _session_factory: sessionmaker[AsyncSession] = async_session_maker

    @classmethod
    async def get_session(cls) -> AsyncSession:
        """
        Получить новую асинхронную сессию.

        :return: Экземпляр `AsyncSession`.
        """
        return cls._session_factory()

    @classmethod
    async def get_all_items(cls) -> List[TModel]:
        """
        Получить все объекты модели.

        :return: Список объектов модели.
        """
        async with await cls.get_session() as session:
            result = await session.execute(select(cls.model))
            return list(result.scalars().all())

    @classmethod
    async def get_item_by_id(cls, item_id: int) -> Optional[TModel]:
        """
        Получить объект по ID.

        :param item_id: Идентификатор объекта.
        :return: Экземпляр модели или None, если не найден.
        """
        async with await cls.get_session() as session:
            return await session.get(cls.model, item_id)

    @classmethod
    async def add(cls, **values: Any) -> TModel:
        """
        Добавить новый объект.

        :param values: Поля модели.
        :return: Созданный объект.
        """
        async with await cls.get_session() as session:
            async with session.begin():
                obj = cls.model(**values)
                session.add(obj)
            return obj

    @classmethod
    async def update(cls, item_id: int, **values: Any) -> Optional[TModel]:
        """
        Обновить объект по ID.

        :param item_id: Идентификатор объекта.
        :param values: Поля для обновления.
        :return: Обновлённый объект или None, если не найден.
        """
        async with await cls.get_session() as session:
            async with session.begin():
                obj = await session.get(cls.model, item_id)
                if not obj:
                    return None
                for k, v in values.items():
                    if hasattr(obj, k):
                        setattr(obj, k, v)
            return obj

    @classmethod
    async def delete(cls, item_id: int) -> Optional[TModel]:
        """
        Удалить объект по ID.

        :param item_id: Идентификатор объекта.
        :return: Удалённый объект или None, если не найден.
        """
        async with await cls.get_session() as session:
            async with session.begin():
                obj = await session.get(cls.model, item_id)
                if not obj:
                    return None
                await session.delete(obj)
            return obj


class UserDAO(BaseDAO[User]):
    """
    DAO для работы с пользователями.
    """

    model = User

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Найти пользователя по email.

        :param email: Электронная почта пользователя.
        :return: Пользователь или None, если не найден.
        """
        async with await self.get_session() as session:
            res = await session.execute(select(User).where(User.email == email))
            return res.scalar_one_or_none()

    async def create_user(self, *, email: str, hashed_password: str) -> User:
        """
        Создать нового пользователя.

        :param email: Электронная почта.
        :param hashed_password: Хэш пароля.
        :return: Созданный пользователь.
        """
        return await self.add(email=email, hashed_password=hashed_password)

    async def exists_by_email(self, email: str) -> bool:
        """
        Проверить, существует ли пользователь с указанным email.

        :param email: Электронная почта.
        :return: True — если существует, False — иначе.
        """
        return (await self.get_user_by_email(email)) is not None


class ResumeDAO(BaseDAO[Resume]):
    """
    DAO для работы с резюме.
    """

    model = Resume

    async def get_all_by_user(self, user_id: int) -> List[Resume]:
        """
        Получить все резюме пользователя.

        :param user_id: ID пользователя.
        :return: Список резюме.
        """
        async with await self.get_session() as session:
            res = await session.execute(select(Resume).where(Resume.user_id == user_id))
            return list(res.scalars().all())

    async def get_by_id_for_user(self, res_id: int, user_id: int) -> Optional[Resume]:
        """
        Получить резюме по ID для конкретного пользователя.

        :param res_id: ID резюме.
        :param user_id: ID пользователя.
        :return: Резюме или None, если не найдено/не принадлежит пользователю.
        """
        async with await self.get_session() as session:
            res = await session.execute(
                select(Resume).where(Resume.id == res_id, Resume.user_id == user_id)
            )
            return res.scalar_one_or_none()

    async def add_for_user(self, *, user_id: int, title: str, content: str) -> Resume:
        """
        Добавить новое резюме для пользователя.

        :param user_id: ID пользователя.
        :param title: Заголовок резюме.
        :param content: Содержимое резюме.
        :return: Созданное резюме.
        """
        return await self.add(user_id=user_id, title=title, content=content)

    async def update_for_user(self, *, res_id: int, user_id: int, **fields: Any) -> Optional[Resume]:
        """
        Обновить резюме только у его владельца.

        :param res_id: ID резюме.
        :param user_id: ID пользователя.
        :param fields: Поля для обновления.
        :return: Обновлённое резюме или None, если не найдено/не принадлежит пользователю.
        """
        async with await self.get_session() as session:
            async with session.begin():
                res = await session.execute(
                    select(Resume).where(Resume.id == res_id, Resume.user_id == user_id)
                )
                obj = res.scalar_one_or_none()
                if not obj:
                    return None
                for k, v in fields.items():
                    if hasattr(obj, k):
                        setattr(obj, k, v)
            return obj

    async def delete_for_user(self, *, res_id: int, user_id: int) -> Optional[Resume]:
        """
        Удалить резюме только у его владельца.

        :param res_id: ID резюме.
        :param user_id: ID пользователя.
        :return: Удалённое резюме или None, если не найдено/не принадлежит пользователю.
        """
        async with await self.get_session() as session:
            async with session.begin():
                res = await session.execute(
                    select(Resume).where(Resume.id == res_id, Resume.user_id == user_id)
                )
                obj = res.scalar_one_or_none()
                if not obj:
                    return None
                await session.delete(obj)
            return obj
