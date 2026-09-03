from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


_engine = None
_SessionLocal = None


def configure(database_url: str) -> None:
    global _engine, _SessionLocal

    if database_url.startswith("sqlite"):
        # StaticPool ensures all connections share one in-memory DB in tests
        _engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        _engine = create_engine(database_url)

    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def get_engine():
    return _engine


def create_tables() -> None:
    Base.metadata.create_all(bind=_engine)


def get_db() -> Generator[Session, None, None]:
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
