from flask import jsonify, make_response, request

from app import db
from app.auth.csrf import csrf_token_required
from app.models.refresh_token import RefreshToken

from . import bp
from . import errors as TokenError
from .utils import generate_access_token


@bp.route("/refresh_access_token", methods=["POST"])
@csrf_token_required
def refresh_access_token():
    if not ("refresh_token" in request.cookies and "access_token"):
        return jsonify({"message": "invalid tokens"}), 401

    access_token = request.cookies["access_token"]
    refresh_token = request.cookies["refresh_token"]

    if not (access_token and refresh_token):
        return jsonify({"message": "invalid tokens"}), 401

    new_access_token = ""

    try:
        new_access_token = generate_access_token(refresh_token, access_token)
        db.session.commit()
    except TokenError.InvalidTokenError:
        return jsonify({"message": "invalid token provided"}), 401
    except TokenError.RevokedTokenError:
        return jsonify({"message": "refresh token has been revoked"}), 401
    except TokenError.TokenCompromisedError:
        RefreshToken.revoke_token(refresh_token)
        db.session.commit()
        return jsonify({"message": "compromised refresh token"}), 401
    except TokenError.AccessTokenNotExpiredError:
        RefreshToken.revoke_token(refresh_token)
        db.session.commit()
        return jsonify({
            "message": "user might be compromised, access revoked"
        }), 401

    response = make_response(
        jsonify({
            "message": "new access token generated"
        }))
    response.set_cookie("access_token", new_access_token, httponly=True)

    return response
