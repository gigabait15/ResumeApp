from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class User(Base):
    """
    Модель пользователя системы.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя (PK).
        email (str): Электронная почта пользователя (уникальная, обязательная).
        hashed_password (str): Хэшированный пароль пользователя.
        resumes (list[Resume]): Список резюме, принадлежащих пользователю.
    """

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Уникальный идентификатор пользователя"
    )
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        doc="Электронная почта пользователя (уникальная)"
    )
    hashed_password: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Хэшированный пароль пользователя"
    )

    resumes: Mapped[list["Resume"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        doc="Связанные резюме пользователя"
    )


class Resume(Base):
    """
    Модель резюме.

    Атрибуты:
        id (int): Уникальный идентификатор резюме (PK).
        title (str): Заголовок резюме.
        content (str): Содержимое резюме.
        user_id (int): Внешний ключ на пользователя-владельца.
        user (User): Связанный объект пользователя.
    """

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Уникальный идентификатор резюме"
    )
    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Заголовок резюме"
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Содержимое резюме"
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        nullable=False,
        doc="Внешний ключ на пользователя-владельца"
    )
    user: Mapped["User"] = relationship(
        back_populates="resumes",
        doc="Пользователь, которому принадлежит резюме"
    )
