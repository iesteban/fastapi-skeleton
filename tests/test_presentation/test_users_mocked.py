"""
Examples of how to use mocks in tests.

The presentation layer is tested here in full isolation: the database is never
touched because UserService is replaced with a mock object.

Note: in FastAPI the db session is injected via Depends(get_db). The conftest
already overrides that dependency, but since UserService is mocked entirely
here, the db session is never forwarded to it — so no DB is needed at all.
"""
from unittest.mock import MagicMock, patch

SERVICE = "app.presentation.users.UserService"


class TestCreateUserWithMock:
    def test_returns_201_with_mocked_service(self, client):
        """Patch the service so no DB call is made."""
        fake_user = MagicMock(id=1, username="alice", email="alice@example.com")

        with patch(f"{SERVICE}.create_user", return_value=fake_user) as mock_create:
            resp = client.post("/users/", json={"username": "alice", "email": "alice@example.com"})

        assert resp.status_code == 201
        assert resp.json() == {"id": 1, "username": "alice", "email": "alice@example.com"}
        # Assert the service was called with the right arguments
        mock_create.assert_called_once()
        _, kwargs = mock_create.call_args
        assert kwargs["username"] == "alice"
        assert kwargs["email"] == "alice@example.com"

    def test_returns_409_when_service_raises_conflict(self, client):
        """Make the mock raise a domain exception."""
        from app.business.users import UserAlreadyExistsError

        with patch(f"{SERVICE}.create_user", side_effect=UserAlreadyExistsError("taken")):
            resp = client.post("/users/", json={"username": "alice", "email": "alice@example.com"})

        assert resp.status_code == 409
        assert "taken" in resp.json()["detail"]

    def test_service_not_called_when_validation_fails(self, client):
        """Pydantic rejects the request before the service is ever reached."""
        with patch(f"{SERVICE}.create_user") as mock_create:
            resp = client.post("/users/", json={"username": "x", "email": "bad"})

        assert resp.status_code == 422
        mock_create.assert_not_called()


class TestGetUserWithMock:
    def test_returns_200_with_mocked_service(self, client):
        fake_user = MagicMock(id=7, username="bob", email="bob@example.com")

        with patch(f"{SERVICE}.get_user", return_value=fake_user):
            resp = client.get("/users/7")

        assert resp.status_code == 200
        assert resp.json()["username"] == "bob"

    def test_returns_404_when_service_raises_not_found(self, client):
        from app.business.users import UserNotFoundError

        with patch(f"{SERVICE}.get_user", side_effect=UserNotFoundError("not found")):
            resp = client.get("/users/99")

        assert resp.status_code == 404


class TestPatchAsDecorator:
    """Same patterns as above but using @patch decorator syntax."""

    @patch(f"{SERVICE}.create_user")
    def test_create_called_with_correct_args(self, mock_create, client):
        mock_create.return_value = MagicMock(id=2, username="carol", email="carol@example.com")

        client.post("/users/", json={"username": "carol", "email": "carol@example.com"})

        mock_create.assert_called_once()
        _, kwargs = mock_create.call_args
        assert kwargs["username"] == "carol"

    @patch(f"{SERVICE}.get_user")
    def test_get_delegates_to_service(self, mock_get, client):
        mock_get.return_value = MagicMock(id=3, username="dave", email="dave@example.com")

        resp = client.get("/users/3")

        mock_get.assert_called_once()
        assert resp.status_code == 200
