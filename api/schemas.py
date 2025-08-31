from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegistration(BaseModel):
    """
    Схема регистрации нового пользователя.
    """
    email: EmailStr = Field(..., description="Электронная почта пользователя")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Пароль (от 8 до 128 символов)"
    )


class UserLogin(BaseModel):
    """
    Схема входа пользователя в систему.
    """
    email: EmailStr = Field(..., description="Электронная почта пользователя")
    password: str = Field(..., description="Пароль")


class Token(BaseModel):
    """
    Схема токена доступа (JWT).
    """
    access_token: str = Field(..., description="JWT-токен доступа")
    token_type: str = Field("bearer", description="Тип токена (обычно 'bearer')")
    expires_at: datetime = Field(..., description="Время истечения срока действия токена")


class ResumeCreate(BaseModel):
    """
    Схема создания нового резюме.
    """
    title: str = Field(..., description="Заголовок резюме")
    content: str = Field(..., description="Содержимое резюме")


class ResumeUpdate(BaseModel):
    """
    Схема обновления резюме.
    Поля являются необязательными, обновляются только переданные значения.
    """
    title: str | None = Field(None, description="Новый заголовок резюме")
    content: str | None = Field(None, description="Новое содержимое резюме")


class ResumeOut(BaseModel):
    """
    Схема возврата резюме из БД (на чтение).
    """
    id: int = Field(..., description="ID резюме")
    title: str = Field(..., description="Заголовок резюме")
    content: str = Field(..., description="Содержимое резюме")

    model_config = ConfigDict(from_attributes=True)
