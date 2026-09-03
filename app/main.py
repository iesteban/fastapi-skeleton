from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import config
from .database import configure, create_tables
from .presentation import users_router


def create_app(env: str = "default") -> FastAPI:
    cfg = config[env]
    configure(cfg.DATABASE_URL)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        create_tables()
        yield

    app = FastAPI(lifespan=lifespan)
    app.include_router(users_router, prefix="/users", tags=["users"])
    return app
