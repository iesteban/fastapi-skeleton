import pytest

from app.business import UserService
from app.business.users import UserAlreadyExistsError, UserNotFoundError


class TestUserServiceCreate:
    def test_creates_user(self, db):
        user = UserService.create_user(db, "frank", "frank@example.com")
        assert user.id is not None
        assert user.username == "frank"

    def test_raises_on_duplicate_username_case_insensitive(self, db):
        UserService.create_user(db, "Grace", "grace@example.com")
        with pytest.raises(UserAlreadyExistsError):
            UserService.create_user(db, "grace", "other@example.com")

    def test_raises_on_duplicate_email_case_insensitive(self, db):
        UserService.create_user(db, "henry", "Henry@example.com")
        with pytest.raises(UserAlreadyExistsError):
            UserService.create_user(db, "henry2", "henry@example.com")


class TestUserServiceGet:
    def test_returns_existing_user(self, db):
        created = UserService.create_user(db, "iris", "iris@example.com")
        fetched = UserService.get_user(db, created.id)
        assert fetched.id == created.id

    def test_raises_for_missing_user(self, db):
        with pytest.raises(UserNotFoundError):
            UserService.get_user(db, 99999)
