from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings


def _engine_url_and_pool():
    p = (settings.sqlite_path or "").strip()
    if p == ":memory:":
        return (
            "sqlite:///:memory:",
            {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool},
        )
    return (
        f"sqlite:///{p}",
        {"connect_args": {"check_same_thread": False}},
    )


_url, _kw = _engine_url_and_pool()
engine = create_engine(_url, **_kw)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
