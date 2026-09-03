import os


class Config:
    DATABASE_URL: str


class DevelopmentConfig(Config):
    DATABASE_URL = os.environ.get(
        "DATABASE_URL", "postgresql://fastapi:fastapi@db:5432/fastapi_dev"
    )


class TestingConfig(Config):
    DATABASE_URL = "sqlite:///:memory:"


class ProductionConfig(Config):
    DATABASE_URL = os.environ.get("DATABASE_URL")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
