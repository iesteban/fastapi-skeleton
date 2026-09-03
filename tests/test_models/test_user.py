import pytest
from sqlalchemy.exc import IntegrityError

from app.models import User


class TestUserModel:
    def test_persists_with_valid_data(self, db):
        user = User(username="jack", email="jack@example.com")
        db.add(user)
        db.commit()
        assert user.id is not None
        assert user.created_at is not None

    def test_raises_on_null_username(self, db):
        db.add(User(email="noname@example.com"))
        with pytest.raises(IntegrityError):
            db.commit()

    def test_raises_on_null_email(self, db):
        db.add(User(username="nomail"))
        with pytest.raises(IntegrityError):
            db.commit()

    def test_raises_on_duplicate_username(self, db):
        db.add(User(username="kate", email="kate@example.com"))
        db.commit()
        db.add(User(username="kate", email="kate2@example.com"))
        with pytest.raises(IntegrityError):
            db.commit()
