from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    unhandled_exception_handler,
)
from app.core.logging import logger, setup_logging
from app.core.startup import validate_startup

import os


# Configure logging once
setup_logging()

# Validate configuration before the application starts
validate_startup()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


# Frontend integration
# Allows local Next.js development server to call FastAPI APIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)


app.add_exception_handler(
    AppException,
    app_exception_handler,
)

app.add_exception_handler(
    Exception,
    unhandled_exception_handler,
)

import os

print("LANGSMITH_TRACING:", os.getenv("LANGSMITH_TRACING"))
print("LANGSMITH_PROJECT:", os.getenv("LANGSMITH_PROJECT"))
print(
    "LANGSMITH_API_KEY:",
    bool(os.getenv("LANGSMITH_API_KEY")),
)
logger.info("Application starting...")