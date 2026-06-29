from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError as PydanticValidationError

from app.core.config import get_settings
from app.core.exception_handlers import app_exception_handler, request_validation_exception_handler
from app.core.exceptions import AppException
from app.core.logging import configure_logging
from app.routers import menu_items, orders

configure_logging()

app = FastAPI(
    title="Mayker Order Tool API",
    version="0.1.0",
    description="Group food-ordering API for Mayker Order Tool",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(PydanticValidationError, request_validation_exception_handler)  # type: ignore[arg-type]

# Routers
app.include_router(orders.router)
app.include_router(menu_items.router)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}
