from flask import current_app, jsonify, make_response, request
from sqlalchemy import or_

from app import db
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.auth.csrf import set_csrf_token_cookie
from app.token_schema import (access_token_required, get_current_user,
                              set_token_cookies)

from . import bp
from .csrf import csrf_token_required
from .utils import user_not_logged


@bp.route("/register", methods=["POST"])
@user_not_logged
def register_user():
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    #TODO: validate data
    user_username = User.first(username=username)
    user_email = User.first(email=email)

    if user_username is not None:
        return jsonify({
            "message": f"{username} has already been registered"
        }), 422

    if user_email is not None:
        return jsonify({
            "message": f"{email} has already been registered"
        }), 422

    if password != confirm_password:
        return jsonify({"message": "passwords don't match"}), 422

    try:
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
    except:
        return jsonify({
            "message":
                "an error has ocurred while registering, please try again"
        }), 500

    response = make_response(jsonify({"message": "successfully registered"}))
    set_token_cookies(response, user.username)
    set_csrf_token_cookie(response)
    return response


@bp.route("/login", methods=["POST"])
@user_not_logged
def login():
    user_id = request.form["id"]
    password = request.form["password"]

    if not user_id:
        return jsonify({"message": "no username or email provided"}), 422

    if not password:
        return jsonify({"message": "no password provided"}), 422

    user = User.query.filter(
        or_(User.username == user_id, User.email == user_id)).first()

    if user is None:
        return jsonify({
            "message": f"no user with username or email {id} found"
        }), 404

    if not user.check_password(password):
        return jsonify({"message": "invalid credentials"}), 401

    response = make_response(jsonify({"message": "logged in successfully"}))
    set_token_cookies(response, user.username)
    set_csrf_token_cookie(response)
    return response


@bp.route("/logout", methods=["POST"])
@csrf_token_required
@access_token_required
def logout():
    user_id = get_current_user()
    RefreshToken.revoke_user_tokens(user_id)
    db.session.commit()
    response = make_response(jsonify({"message": "logout successful"}))

    access_cookie_name = current_app.config["ACCESS_COOKIE_NAME"]
    refresh_cookie_name = current_app.config["REFRESH_COOKIE_NAME"]
    csrf_cookie_name = current_app.config["CSRF_COOKIE_NAME"]
    secure_token_cookies = current_app.config["SECURE_TOKEN_COOKIES"]

    response.set_cookie(
        access_cookie_name, "", secure=secure_token_cookies, httponly=True)
    response.set_cookie(
        refresh_cookie_name, "", secure=secure_token_cookies, httponly=True)
    response.set_cookie(
        csrf_cookie_name, "", secure=secure_token_cookies, httponly=True)

    return response
