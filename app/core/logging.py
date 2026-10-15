import logging.config

from app.core.config import settings


def configure_logging() -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {"handlers": ["console"], "level": settings.log_level},
            "loggers": {
                "uvicorn.access": {"level": "WARNING" if settings.is_production else "INFO"},
                "sqlalchemy.engine": {"level": "INFO" if settings.db_echo else "WARNING"},
            },
        }
    )
