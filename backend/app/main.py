from fastapi import FastAPI
from app.api.router import api_router

from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    unhandled_exception_handler,
)
from app.core.logging import logger, setup_logging

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)
app.include_router(api_router)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

logger.info("Application starting...")