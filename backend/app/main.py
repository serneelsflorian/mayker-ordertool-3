from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

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

# CORS middleware — origins resolved lazily so unit-test imports don't require DATABASE_URL
def _get_cors_origins() -> list[str]:
    try:
        return get_settings().CORS_ORIGINS
    except Exception:
        return ["http://localhost:5173"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)  # type: ignore[arg-type]

# Routers
app.include_router(orders.router)
app.include_router(menu_items.router)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}
