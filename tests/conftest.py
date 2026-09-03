import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db, get_engine
from app.main import create_app


@pytest.fixture(scope="session")
def app():
    _app = create_app("testing")
    # create_tables() runs via lifespan on first TestClient use,
    # but we also need tables for non-client fixtures (business/model tests)
    Base.metadata.create_all(bind=get_engine())
    return _app


@pytest.fixture()
def db(app):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    session = SessionLocal()
    yield session
    session.rollback()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()


@pytest.fixture()
def client(app, db):
    # Override get_db so route handlers share the same session as the test
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
