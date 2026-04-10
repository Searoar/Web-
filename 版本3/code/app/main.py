from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.exception_handlers import http_exception_handler, request_validation_exception_handler
from app.routers import health, journeys, locations, transport_ref
from app.seed import seed_reference_data


def _run_migrations_or_create_all() -> None:
    """文件库使用 Alembic；:memory:（pytest）直接用 metadata.create_all 与迁移共用同一引擎。"""
    if (settings.sqlite_path or "").strip() == ":memory:":
        Base.metadata.create_all(bind=engine)
        return
    cfg = Config(str(Path(__file__).resolve().parent.parent / "alembic.ini"))
    command.upgrade(cfg, "head")


@asynccontextmanager
async def lifespan(_: FastAPI):
    _run_migrations_or_create_all()
    db = SessionLocal()
    try:
        seed_reference_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)

app.include_router(health.router)
app.include_router(journeys.router)
app.include_router(locations.router)
app.include_router(transport_ref.router)
