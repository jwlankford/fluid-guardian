"""Configurable SQLAlchemy engine and session helpers."""

from contextlib import contextmanager
import os
from collections.abc import Iterator
import sys
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from fg_core.db.base import Base


def _create_engine(database_url: str, **engine_options: Any) -> Engine:
    if database_url.startswith("sqlite:"):
        engine_options.setdefault("connect_args", {"check_same_thread": False})
    elif database_url.startswith("postgres://"):
        database_url = "postgresql+psycopg://" + database_url.removeprefix("postgres://")
    elif database_url.startswith("postgresql://"):
        database_url = "postgresql+psycopg://" + database_url.removeprefix("postgresql://")
    return create_engine(database_url, **engine_options)


DATABASE_URL = os.getenv("FG_DATABASE_URL", "sqlite:///./fg_core.db")
engine = _create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def configure_database(database_url: str, **engine_options: Any) -> Engine:
    """Replace the module's engine and session factory with the configured database."""
    global engine, SessionLocal
    engine.dispose()
    engine = _create_engine(database_url, **engine_options)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db_package = sys.modules.get("fg_core.db")
    if db_package is not None:
        db_package.engine = engine
        db_package.SessionLocal = SessionLocal
    core_package = sys.modules.get("fg_core")
    if core_package is not None:
        core_package.SessionLocal = SessionLocal
    return engine


def create_all(bind: Engine | None = None) -> None:
    """Create tables for all registered shared entities."""
    from fg_core import models  # noqa: F401

    Base.metadata.create_all(bind=bind or engine)


def get_session() -> Iterator[Session]:
    """Yield a session suitable for framework dependency injection."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a session that commits on success and rolls back on failure."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
