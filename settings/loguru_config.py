"""
Конфигурация логирования приложения.

Особенности:
- Используется библиотека Loguru.
- Логи разделяются по уровням (DEBUG, INFO, WARNING, ERROR, CRITICAL) в разные файлы.
- Отдельный файл для access-логов Uvicorn.
- Автоматическая ротация, хранение и сжатие логов.
- Перенаправление стандартного `logging` и логов FastAPI/Uvicorn в Loguru.
"""

import logging
from pathlib import Path

from loguru import logger

# --- Настройки директорий и файлов ---
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "DEBUG": LOG_DIR / "debug.log",
    "INFO": LOG_DIR / "info.log",
    "WARNING": LOG_DIR / "warning.log",
    "ERROR": LOG_DIR / "error.log",
    "CRITICAL": LOG_DIR / "critical.log",
    "ACCESS": LOG_DIR / "access.log",
}

# --- Параметры логов ---
ROTATION = "10 MB"       # Максимальный размер файла до ротации
RETENTION = "10 days"    # Время хранения логов
COMPRESSION = "zip"      # Формат сжатия старых логов
ENCODING = "utf-8"       # Кодировка лог-файлов


def exact_level(level_name: str):
    """
    Фильтр для логов: пропускает ТОЛЬКО записи с указанным уровнем.

    :param level_name: Уровень логирования (например, "INFO").
    :return: Функция-фильтр для Loguru.
    """

    def _filter(record):
        return record["level"].name == level_name

    return _filter


def only_uvicorn_access(record):
    """
    Фильтр: только access-логи uvicorn (HTTP-запросы).

    :param record: Запись лога.
    :return: True, если лог принадлежит `uvicorn.access`.
    """
    return record["name"].startswith("uvicorn.access")


# --- Настройка Loguru ---
logger.remove()  # удаляем стандартный sink (stdout)

# Логи по уровням
for lvl in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
    logger.add(
        FILES[lvl],
        level="DEBUG",  # захватываем все уровни, фильтруем вручную
        filter=exact_level(lvl),
        rotation=ROTATION,
        retention=RETENTION,
        compression=COMPRESSION,
        encoding=ENCODING,
        enqueue=True,  # безопасная запись из разных потоков
    )

# Отдельный лог-файл для access-логов Uvicorn
logger.add(
    FILES["ACCESS"],
    level="DEBUG",
    filter=only_uvicorn_access,
    rotation=ROTATION,
    retention=RETENTION,
    compression=COMPRESSION,
    encoding=ENCODING,
    enqueue=True,
)


class InterceptHandler(logging.Handler):
    """
    Хэндлер для перехвата логов из стандартного модуля `logging`
    и перенаправления их в Loguru.
    """

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


# Перенастройка стандартного logging
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# Перенаправляем логи FastAPI и Uvicorn в Loguru
for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
    logging.getLogger(name).handlers = [InterceptHandler()]
    logging.getLogger(name).propagate = False
