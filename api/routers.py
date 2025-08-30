from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from api.schemas import (ResumeCreate, ResumeOut, ResumeUpdate, Token,
                         UserLogin, UserRegistration)
from database.crud import ResumeDAO, UserDAO
from services.auth_service import (create_access_token, get_current_user,
                                   hash_password, verify_password)

userdb = UserDAO()
resumedb = ResumeDAO()


router = APIRouter(tags=["API"], prefix="/api")
"""Публичные эндпоинты для регистрации и авторизации пользователей.
Позволяют создать нового пользователя и получить JWT-токен доступа.
"""


@router.post("/user/registration", response_model=Token)
async def register(body: UserRegistration) -> Token:
    """
    Зарегистрировать нового пользователя.

    - Проверяет уникальность e-mail.
    - Хэширует пароль и создаёт пользователя.
    - Возвращает JWT-токен доступа.

    :param body: Данные регистрации пользователя (e-mail и пароль).
    :raises HTTPException: 400 — если пользователь с таким e-mail уже существует.
    :return: Объект `Token` с access token.
    """
    if await userdb.get_user_by_email(str(body.email)):
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    hashed = hash_password(body.password)
    await userdb.create_user(email=str(body.email), hashed_password=hashed)
    return create_access_token(sub=str(body.email))


@router.post("/user/login", response_model=Token)
async def login(body: UserLogin) -> Token:
    """
    Выполнить вход пользователя.

    - Ищет пользователя по e-mail.
    - Проверяет пароль.
    - Возвращает JWT-токен доступа.

    :param body: Данные для входа (e-mail и пароль).
    :raises HTTPException: 401 — если пара e-mail/пароль неверна.
    :return: Объект `Token` с access token.
    """
    user = await userdb.get_user_by_email(str(body.email))
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    return create_access_token(sub=str(body.email))


protected_resume_router = APIRouter(
    prefix="/resume",
    tags=["resume"],
    dependencies=[Depends(get_current_user)],
)
"""Защищённые эндпоинты для работы с резюме.
Доступны только авторизованным пользователям (с JWT-токеном).
Позволяют создавать, просматривать, редактировать и удалять резюме.
"""


@protected_resume_router.get("/", response_model=List[ResumeOut])
async def list_resumes(current_user: Any = Depends(get_current_user)) -> List[ResumeOut]:
    """
    Получить список всех резюме текущего пользователя.

    :param current_user: Текущий пользователь (инъекция через Depends).
    :return: Список резюме в формате `ResumeOut`.
    """
    return await resumedb.get_all_by_user(current_user.id)


@protected_resume_router.post("/", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
async def create_resume(body: ResumeCreate, current_user: Any = Depends(get_current_user)) -> ResumeOut:
    """
    Создать новое резюме для текущего пользователя.

    :param body: Данные для создания резюме.
    :param current_user: Текущий пользователь.
    :return: Созданное резюме в формате `ResumeOut`.
    """
    return await resumedb.add_for_user(user_id=current_user.id, **body.dict())


@protected_resume_router.get("/{res_id}", response_model=ResumeOut)
async def get_resume(res_id: int, current_user: Any = Depends(get_current_user)) -> ResumeOut:
    """
    Получить резюме по идентификатору.

    :param res_id: Идентификатор резюме.
    :param current_user: Текущий пользователь.
    :raises HTTPException: 404 — если резюме не найдено.
    :return: Резюме в формате `ResumeOut`.
    """
    item = await resumedb.get_by_id_for_user(res_id, current_user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Resume not found")
    return item


@protected_resume_router.get("/{res_id}/improve", response_model=ResumeOut)
async def improve_resume(res_id: int, current_user: Any = Depends(get_current_user)) -> ResumeOut:
    """
    Вернуть «улучшенную» версию резюме (без сохранения в базу).

    Техническое примечание: эндпоинт демонстрационный — он не изменяет запись в БД,
    а лишь модифицирует поле `content` на лету и возвращает результат.

    :param res_id: Идентификатор резюме.
    :param current_user: Текущий пользователь.
    :raises HTTPException: 404 — если резюме не найдено.
    :return: Резюме с модифицированным полем `content` в формате `ResumeOut`.
    """
    item: Dict[str, Any] = await resumedb.get_by_id_for_user(res_id, current_user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {**item, "content": f"{item.get('content', '')} [Improved]"}


@protected_resume_router.put("/{res_id}", response_model=ResumeOut)
async def update_resume(res_id: int, body: ResumeUpdate, current_user: Any = Depends(get_current_user)) -> ResumeOut:
    """
    Обновить поля резюме.

    Пустые/None-поля из тела запроса игнорируются, обновляются только переданные значения.

    :param res_id: Идентификатор резюме.
    :param body: Данные обновления.
    :param current_user: Текущий пользователь.
    :raises HTTPException:
        - 400 — если нет ни одного поля для обновления;
        - 404 — если резюме не найдено.
    :return: Обновлённое резюме в формате `ResumeOut`.
    """
    data = {k: v for k, v in body.dict().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="Nothing to update")
    item = await resumedb.update_for_user(res_id=res_id, user_id=current_user.id, **data)
    if not item:
        raise HTTPException(status_code=404, detail="Resume not found")
    return item


@protected_resume_router.delete("/{res_id}", response_model=ResumeOut)
async def delete_resume(res_id: int, current_user: Any = Depends(get_current_user)) -> ResumeOut:
    """
    Удалить резюме.

    :param res_id: Идентификатор резюме.
    :param current_user: Текущий пользователь.
    :raises HTTPException: 404 — если резюме не найдено.
    :return: Удалённое резюме (как подтверждение) в формате `ResumeOut`.
    """
    item = await resumedb.delete_for_user(res_id=res_id, user_id=current_user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Resume not found")
    return item
