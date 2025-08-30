from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, security, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from api.schemas import Token
from database.crud import UserDAO
from settings.config import jwtsettings

oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl="/api/user/login")
userdb = UserDAO()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(raw: str) -> str:
    """
    Захэшировать пароль.

    :param raw: Пароль в открытом виде.
    :return: Хэш пароля.
    """
    return pwd_context.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    """
    Проверить соответствие пароля и хэша.

    :param raw: Пароль в открытом виде.
    :param hashed: Хэш пароля.
    :return: True — если пароль совпадает, False — иначе.
    """
    return pwd_context.verify(raw, hashed)


def create_access_token(sub: str, expires_minutes: int = jwtsettings.ACCESS_TOKEN_EXPIRE_MIN) -> Token:
    """
    Создать JWT-токен доступа.

    :param sub: Идентификатор субъекта (обычно email пользователя).
    :param expires_minutes: Время жизни токена в минутах.
    :return: Объект `Token` с токеном доступа, временем истечения и типом.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_minutes)
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp())
    }
    token = jwt.encode(payload, jwtsettings.JWT_SECRET, algorithm=jwtsettings.JWT_ALG)
    return Token(access_token=token, expires_at=expire)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Получить текущего пользователя по JWT-токену.

    :param token: JWT-токен (берётся из заголовка Authorization: Bearer).
    :raises HTTPException:
        - 401, если токен отсутствует, неверен или просрочен.
        - 401, если пользователь из токена не найден.
    :return: Пользователь из базы данных.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    try:
        payload = jwt.decode(token, jwtsettings.JWT_SECRET, algorithms=[jwtsettings.JWT_ALG])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await userdb.get_user_by_email(str(sub))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
