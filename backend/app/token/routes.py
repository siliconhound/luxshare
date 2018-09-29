from flask import jsonify, make_response, request, current_app

from app import db
from app.auth.csrf import csrf_token_required
from app.models.refresh_token import RefreshToken
from app.token_schema import (
    get_refresh_token_from_cookie, get_access_token_from_cookie,
    create_fresh_access_token, TokensCompromisedError, InvalidAccessTokenError,
    InvalidRefreshTokenError)

from . import bp


@bp.route("/refresh_access_token", methods=["POST"])
@csrf_token_required
def refresh_access_token():
    try:
        refresh_token = get_refresh_token_from_cookie()
        access_token = get_access_token_from_cookie()

        if not (access_token and refresh_token):
            return jsonify({"message": "invalid tokens"}), 401

    except KeyError:
        return jsonify({"message": "invalid tokens"}), 401

    new_access_token = ""

    try:
        new_access_token = create_fresh_access_token(refresh_token,
                                                     access_token)
    except (InvalidAccessTokenError, InvalidRefreshTokenError):
        return jsonify({"message": "invalid token provided"}), 401
    except TokensCompromisedError:
        RefreshToken.revoke_token(refresh_token)
        db.session.commit()
        return jsonify({"message": "compromised tokens"}), 401

    response = make_response(
        jsonify({
            "message": "new access token generated"
        }))
    response.set_cookie(
        current_app.config["ACCESS_COOKIE_NAME"],
        new_access_token,
        secure=current_app.config["SECURE_TOKEN_COOKIES"],
        httponly=True)

    return response