from uuid import uuid4
from datetime import datetime, timedelta

from app import db
from app.auth.csrf import generate_csrf_token
from app.models.refresh_token import RefreshToken
from app.models.user import User

from helpers import get_cookie


def test_refresh_token(app, client):
    with app.app_context():
        user = User(username="test", email="test@example.com", password="test")
        db.session.add(user)
        access_token = generate_token(user.username, expires_in=-60)
        refresh_token = RefreshToken(
            token=str(uuid4()),
            user_id=user.username,
            mapped_token=access_token)
        db.session.add(refresh_token)
        db.session.commit()
        refresh_token = refresh_token.token

    client.set_cookie("localhost", "access_token", access_token, httponly=True)
    client.set_cookie(
        "localhost", "refresh_token", refresh_token, httponly=True)

    csrf_token = generate_csrf_token()
    client.set_cookie("localhost", "x-csrf-token", csrf_token, httponly=True)

    response = client.post(
        "/token/refresh_access_token", headers={"x-csrf-token": csrf_token})

    assert response.status_code == 200
    assert get_cookie(response, "access_token")


def test_revoked_refresh_token(app, client):
    with app.app_context():
        user = User(username="test", email="test@example.com", password="test")
        db.session.add(user)
        access_token = generate_token(user.username, expires_in=-60)
        refresh_token = RefreshToken(
            token=str(uuid4()),
            user_id=user.username,
            mapped_token=access_token,
            revoked=True)
        db.session.add(refresh_token)
        db.session.commit()
        refresh_token = refresh_token.token

    client.set_cookie("localhost", "access_token", access_token, httponly=True)
    client.set_cookie(
        "localhost", "refresh_token", refresh_token, httponly=True)

    csrf_token = generate_csrf_token()
    client.set_cookie("localhost", "x-csrf-token", csrf_token, httponly=True)

    response = client.post(
        "/token/refresh_access_token", headers={"x-csrf-token": csrf_token})

    assert response.status_code == 401
    assert response.get_json()["message"] == "invalid token provided"


def test_compromised_refresh_token(app, client):

    with app.app_context():
        user = User(username="test", email="test@example.com", password="test")
        db.session.add(user)
        access_token = generate_token(user.username)
        refresh_token = RefreshToken(
            token=str(uuid4()),
            user_id=user.username,
            mapped_token=access_token)
        db.session.add(refresh_token)
        db.session.commit()

        refresh_token = refresh_token.token
        attacker_refresh_token = generate_token("test", expires_in=-60)

    csrf_token = generate_csrf_token()

    # attacker request
    client.set_cookie("localhost", "x-csrf-token", csrf_token, httponly=True)
    client.set_cookie(
        "localhost", "access_token", attacker_refresh_token, httponly=True)
    client.set_cookie(
        "localhost", "refresh_token", refresh_token, httponly=True)

    response = client.post(
        "/token/refresh_access_token", headers={"x-csrf-token": csrf_token})

    assert response.status_code == 401
    assert response.get_json()["message"] == "compromised refresh token"


def test_invalid_token(app, client):
    with app.app_context():
        user = User(username="test", email="test@example.com", password="test")
        db.session.add(user)
        access_token = generate_token(user.username, expires_in=-60)
        refresh_token = RefreshToken(
            token=str(uuid4()),
            user_id=user.username,
            mapped_token=access_token,
            expires_at=datetime.utcnow() - timedelta(seconds=60))
        db.session.add(refresh_token)
        db.session.commit()

        refresh_token = refresh_token.token

    csrf_token = generate_csrf_token()

    client.set_cookie("localhost", "x-csrf-token", csrf_token, httponly=True)
    client.set_cookie("localhost", "access_token", access_token, httponly=True)
    client.set_cookie(
        "localhost", "refresh_token", refresh_token, httponly=True)

    response = client.post(
        "/token/refresh_access_token", headers={"x-csrf-token": csrf_token})

    assert response.status_code == 401
    assert response.get_json()["message"] == "invalid token provided"

    with app.app_context():
        refresh_token = RefreshToken.first(token=refresh_token)
        refresh_token.expires_at = datetime.utcnow() + timedelta(days=7)
        db.session.commit()

        refresh_token = refresh_token.token

    csrf_token = generate_csrf_token()

    client.set_cookie("localhost", "x-csrf-token", csrf_token, httponly=True)
    client.set_cookie(
        "localhost",
        "access_token",
        access_token[:int(len(access_token) / 2)],
        httponly=True)
    client.set_cookie(
        "localhost", "refresh_token", refresh_token, httponly=True)

    response = client.post(
        "/token/refresh_access_token", headers={"x-csrf-token": csrf_token})

    assert response.status_code == 401
    assert response.get_json()["message"] == "invalid token provided"


def test_expired_access_token(app, client):
    with app.app_context():
        user = User(username="test", email="test@example.com", password="test")
        db.session.add(user)
        access_token = generate_token(user.username, expires_in=-60)
        refresh_token = RefreshToken(
            token=str(uuid4()),
            user_id=user.username,
            mapped_token=access_token)
        db.session.add(refresh_token)
        db.session.commit()

        refresh_token = refresh_token.token

    csrf_token = generate_csrf_token()

    client.set_cookie("localhost", "x-csrf-token", csrf_token, httponly=True)
    client.set_cookie("localhost", "access_token", access_token, httponly=True)
    client.set_cookie(
        "localhost", "refresh_token", refresh_token, httponly=True)

    response = client.get("/", headers={"x-csrf-token": csrf_token})
    assert response.status_code == 401
    assert response.get_json()["message"] == "expired access token"