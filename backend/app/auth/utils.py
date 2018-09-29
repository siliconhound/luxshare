import re
from functools import wraps

from flask import g, jsonify, make_response, redirect, request, current_app
from jwt import PyJWTError, ExpiredSignatureError

from app import db
from app.models.refresh_token import RefreshToken
from app.token_schema import (get_access_token_from_cookie,
                              get_refresh_token_from_cookie, decode_jwt)


def user_not_logged(f):
    """decorator to redirect if user is already logged in"""

    @wraps(f)
    def f_wrapper(*args, **kwargs):
        try:
            access_token = get_access_token_from_cookie()
        except KeyError:
            return f(*args, **kwargs)

        try:
            decode_jwt(access_token, current_app.config["JWT_SECRET"],
                       current_app.config["JWT_ALGORITHM"])
        except ExpiredSignatureError:
            return jsonify({"message": "user already logged in"}), 403
        except PyJWTError:
            return f(*args, **kwargs)

        return f(*args, **kwargs)

    return f_wrapper
