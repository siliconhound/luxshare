from datetime import datetime, timedelta
from uuid import uuid4
from functools import wraps

from flask import request, jsonify, current_app


def generate_csrf_token():
    return str(uuid4())


def validate_csrf_token():
    """validate if CSRF cookie and header are valid and equal"""

    if not (current_app.config["CSRF_COOKIE_NAME"] in request.cookies and
            current_app.config["CSRF_COOKIE_NAME"] in request.headers):
        return False

    cookie_csrf_token = request.cookies[current_app.config["CSRF_COOKIE_NAME"]]
    header_csrf_token = request.headers[current_app.config["CSRF_COOKIE_NAME"]]

    if not (cookie_csrf_token and header_csrf_token):
        return False

    if cookie_csrf_token != header_csrf_token:
        return False

    return True


def set_csrf_token_cookie(response):
    """Sets CSRF token to cookie

  :param response: response object
  """
    csrf_token = generate_csrf_token()
    response.set_cookie(
        current_app.config["CSRF_COOKIE_NAME"],
        csrf_token,
        secure=current_app.config["SECURE_TOKEN_COOKIES"],
        httponly=True,
        expires=datetime.utcnow() +
        current_app.config["REFRESH_TOKEN_DURATION"])

    response.set_cookie(
        current_app.config["CSRF_COOKIE_NAME"],
        csrf_token,
        secure=current_app.config["SECURE_TOKEN_COOKIES"],
        expires=datetime.utcnow() +
        current_app.config["REFRESH_TOKEN_DURATION"])


def csrf_token_required(f):

    @wraps(f)
    def f_wrapper(*args, **kwargs):

        if not validate_csrf_token():
            return jsonify({"message": "unauthorized"}), 401

        return f(*args, **kwargs)

    return f_wrapper
