from flask import g

from app.models.user import User
from helpers import get_cookie
from app.models.refresh_token import RefreshToken
from app.auth.csrf import generate_csrf_token
from app import db
from app.token_schema import decode_jwt


def test_register(app, client):

    response = client.post(
        "/auth/register",
        data={
            "username": "test",
            "email": "test@gmail.com",
            "password": "test",
            "confirm_password": "test"
        })

    assert response.status_code == 200

    access_token = get_cookie(response, "access_token")
    refresh_token = get_cookie(response, "refresh_token")

    with app.app_context():
        decode_jwt(access_token, app.config["JWT_SECRET"],
                   app.config["JWT_ALGORITHM"])
        refresh_token_instance = RefreshToken.first(token=refresh_token)
        assert refresh_token_instance.is_valid()

        user = User.first(username="test")
        assert user is not None


def test_login(app, client):
    with app.app_context():
        user = User(username="test", email="test@test.com", password="test")
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/auth/login", data={
            "id": "test",
            "password": "test"
        })

    assert response.status_code == 200
    assert get_cookie(response, "refresh_token")
    assert get_cookie(response, "access_token")
    assert get_cookie(response, "x-csrf-token", flags=["HttpOnly"])
    assert get_cookie(response, "x-csrf-token", except_flags=["HttpOnly"])


def test_logout(app, client):
    with app.app_context():
        user = User(username="test", email="test@test.com", password="test")
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/auth/login", data={
            "id": "test",
            "password": "test"
        })

    csrf_token = generate_csrf_token()
    access_token = get_cookie(response, "access_token")
    refresh_token = get_cookie(response, "refresh_token")
    client.set_cookie("localhost", "x-csrf-token", csrf_token, httponly=True)
    client.set_cookie("localhost", "access_token", access_token, httponly=True)
    client.set_cookie(
        "localhost", "refresh_token", refresh_token, httponly=True)
    response = client.post(
        "/auth/logout", headers={"x-csrf-token": csrf_token})

    assert response.status_code == 200
    assert not get_cookie(response, "access_token")
    assert not get_cookie(response, "refresh_token")
    assert not get_cookie(response, "x-csrf-token")