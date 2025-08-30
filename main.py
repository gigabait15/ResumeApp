import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import protected_resume_router, router
from settings.engine import conn
from settings.loguru_config import logger
from src.settings.config import app_middleware

conn.create_database()

app = FastAPI(
    title="ResumeApp API",
    description="API для регистрации пользователей и работы с резюме.",
    version="1.0.0",
    docs_url="/api_docs",
    redoc_url="/api_redoc",
)


app.add_middleware(CORSMiddleware, **app_middleware)

app.include_router(router)
app.include_router(protected_resume_router)


@app.get("/")
async def root():
    """
    Базовый эндпоинт для проверки доступности API.
    """
    return {"message": "Hello World"}


if __name__ == "__main__":
    logger.info("Starting app...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=bool(os.getenv("DEV", False)),
        log_level="info",
    )
