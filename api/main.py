import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, TypedDict

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from api import exceptions
from api.customer.router import router as customer_router
from api.exception_handlers import (
    handle_already_exists_error,
    handle_not_found_error,
)
from api.settings import Settings


class State(TypedDict):
    _logger: structlog.stdlib.BoundLogger
    _settings: Settings
    _database_engine: AsyncEngine


def create_app(settings: Settings, logger: structlog.stdlib.BoundLogger) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[State]:
        engine = create_async_engine(settings.database_url())
        yield {
            "_settings": settings,
            "_logger": logger,
            "_database_engine": engine,
        }
        await engine.dispose()

    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(exceptions.NotFoundError, handle_not_found_error)
    app.add_exception_handler(
        exceptions.AlreadyExistsError, handle_already_exists_error
    )
    app.include_router(customer_router)
    return app


if __name__ == "__main__":
    settings = Settings()
    structlog.configure(
        processors=[
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(settings.LOG_LEVEL_AS_INT),
    )

    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
            },
        },
        "handlers": {
            "default": {
                "formatter": "json",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "json",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": settings.LOG_LEVEL_AS_INT,
            },
            "uvicorn.error": {
                "level": settings.LOG_LEVEL_AS_INT,
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "level": settings.LOG_LEVEL_AS_INT,
                "propagate": False,
            },
            "weasyprint": {
                "handlers": ["access"],
                "level": logging.CRITICAL,
                "propagate": False,
            },
            "fontTools": {
                "handlers": ["access"],
                "level": logging.CRITICAL,
                "propagate": False,
            },
        },
    }

    logger = structlog.get_logger()
    uvicorn.run(
        create_app(settings=settings, logger=logger),
        port=settings.API_PORT,
        host=settings.API_HOST,
        timeout_keep_alive=settings.API_TIMEOUT,
        log_config=log_config,
    )
