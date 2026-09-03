class TestCreateUser:
    def test_creates_user_successfully(self, client):
        resp = client.post("/users/", json={"username": "alice", "email": "alice@example.com"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert "id" in data

    def test_returns_422_when_username_missing(self, client):
        resp = client.post("/users/", json={"email": "bob@example.com"})
        assert resp.status_code == 422

    def test_returns_422_when_email_invalid(self, client):
        resp = client.post("/users/", json={"username": "bob", "email": "not-an-email"})
        assert resp.status_code == 422

    def test_returns_422_when_username_too_short(self, client):
        resp = client.post("/users/", json={"username": "ab", "email": "ab@example.com"})
        assert resp.status_code == 422

    def test_returns_409_on_duplicate_username(self, client):
        client.post("/users/", json={"username": "carol", "email": "carol@example.com"})
        resp = client.post("/users/", json={"username": "carol", "email": "other@example.com"})
        assert resp.status_code == 409

    def test_returns_409_on_duplicate_email(self, client):
        client.post("/users/", json={"username": "dave", "email": "shared@example.com"})
        resp = client.post("/users/", json={"username": "dave2", "email": "shared@example.com"})
        assert resp.status_code == 409


class TestGetUser:
    def test_returns_user(self, client):
        created = client.post("/users/", json={"username": "eve", "email": "eve@example.com"})
        user_id = created.json()["id"]
        resp = client.get(f"/users/{user_id}")
        assert resp.status_code == 200
        assert resp.json()["username"] == "eve"

    def test_returns_404_for_missing_user(self, client):
        resp = client.get("/users/99999")
        assert resp.status_code == 404
