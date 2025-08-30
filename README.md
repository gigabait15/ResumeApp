# ResumeApp — FastAPI + PostgreSQL + SQLAlchemy + JWT

Сервис для хранения и управления резюме на FastAPI с JWT-авторизацией, PostgreSQL и SQLAlchemy.

- **Регистрация и логин** — с хэшированием паролей.  
- **JWT-токен** — авторизация по `Bearer` в заголовке `Authorization`.  
- **CRUD-операции** — создание, просмотр, обновление и удаление резюме.  
- **Демо-фича** — «улучшение» резюме через отдельный эндпоинт.  
- **Логирование** — через Loguru (отдельные файлы для уровней логов + access).  

---

## Содержание

- [Архитектура и директории](#архитектура-и-директории)  
- [Переменные окружения](#переменные-окружения)  
- [Локальный запуск (без Docker)](#локальный-запуск-без-docker)  
- [Docker и docker-compose](#docker-и-docker-compose)
- [Эндпоинты](#эндпоинты)  
  - [/api/user/registration](#apiuserregistration)  
  - [/api/user/login](#apiuserlogin)  
  - [/resume](#resume)  
- [Логи](#логи)  

---

## Архитектура и директории

``` 
├─ Dockerfile
├─ docker-compose.yml
├─ .dockerignore
├─ README.md
├─ main.py
├─ requirements.txt
└─ src/
├─ api/
│ ├─ routers.py # маршруты FastAPI
│ └─ schemas.py # Pydantic-схемы
├─ database/
│ ├─ models/
│ │ ├─ base.py
│ │ └─ models.py
│ └─ crud.py # DAO-слой
├─ services/
│ └─ auth_service.py # логика аутентификации
├─ settings/
│ ├─ config.py
│ ├─ engine.py # движок SQLAlchemy
│ └─ loguru_config.py # конфигурация логов
```

---
## Переменные окружения

Для **локального** запуска используются файлы:

- `src/.env` — настройки БД  
- `src/.env.jwt` — настройки JWT  

Для **Docker** можно создать `.env` в корне репозитория.

### Параметры БД
| Имя           | Описание      |             
|---------------|---------------|
| `DB_NAME`     | Имя БД        |
| `DB_USER`     | Пользователь  |
| `DB_PASSWORD` | Пароль        |
| `DB_HOST`     | Хост БД       |
| `DB_PORT`     | Порт БД       |          

### Параметры JWT
| Имя                    | Описание                        |
|------------------------|---------------------------------|
| `JWT_SECRET`           | Секрет для подписи JWT          |
| `JWT_ALG`              | Алгоритм                        |
| `ACCESS_TOKEN_EXPIRE_MIN` | TTL access-токена (минуты)   |

---

## Локальный запуск (без Docker)

### Виртуальное окружение и зависимости:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
### Запуск приложения:
```bash
uvicorn main:app --reload
```

### Docker и docker-compose
```bash
docker compose up --build
```

FastAPI: http://127.0.0.1:8000

Swagger: http://127.0.0.1:8000/api_docs

---
## Эндпоинты

- POST /api/user/registration  Регистрация пользователя.
- POST /api/user/login Авторизация пользователя.
- GET /resume/ Список резюме текущего пользователя.
- POST /resume/ Создание резюме.
- GET /resume/{id} Получение резюме по ID.
- PUT /resume/{id} Обновление резюме.
- DELETE /resume/{id} Удаление резюме.
- GET /resume/{id}/improve Возвращает «улучшенную» версию резюме (демо-эндпоинт).

---
## Логи

- logs/debug.log — отладка
- logs/info.log — информационные сообщения
- logs/warning.log — предупреждения
- logs/error.log — ошибки
- logs/critical.log — критические ошибки
- logs/access.log — HTTP-запросы Uvicorn