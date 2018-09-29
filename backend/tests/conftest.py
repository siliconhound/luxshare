import pytest
import tempfile
import os
from app import create_app, db
from config import Config
from datetime import timedelta


@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp()

    class TestConfig(Config):
        TESTING = True
        SECRET_KEY = "you-will-never-guess"
        JWT_SECRET = "super-secret-key"
        JWT_ALGORITHM = "HS256"
        CSRF_COOKIE_NAME = "x-csrf-token"
        REFRESH_TOKEN_DURATION = timedelta(days=30)
        SECURE_TOKEN_COOKIES = False
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
        SQLALCHEMY_TRACK_MODIFICATIONS = False

    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


class AuthActions(object):

    def __init__(self, client, csrf_token=""):
        self._client = client
        self._csrf_token = csrf_token

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={
                "username": username,
                "password": password
            })

    def logout(self):
        return self._client.get(
            "/auth/logout", headers={"x-csrf-token": self._csrf_token})

@pytest.fixture
def auth(client):
    return AuthActions(client)