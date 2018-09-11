from datetime import datetime, timedelta
from uuid import uuid4
from calendar import timegm

import jwt
from flask import current_app, g

from app import db
from app.token.errors import (AccessTokenNotExpiredError, InvalidTokenError,
                              RevokedTokenError, TokenCompromisedError)
from app.models.refresh_token import RefreshToken


def generate_token(user_id, expires_in=60, **kwargs):
    """Generate a JWT token

  :param user_id the user that will own the token
  :param expires_in expiration time in seconds
  """
    secret_key = current_app.config["JWT_SECRET_KEY"]
    return jwt.encode({
        "user_id": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=expires_in),
        **kwargs
    },
                      secret_key,
                      algorithm="HS256").decode("utf-8")


def is_token_expired(exp):
    """verify if token has expired

  :param exp: token expiration date
  """
    return exp < timegm(datetime.utcnow().utctimetuple())


def verify_token(token):
    """Token verification

  if token is valid claims will be available in the jwt_claims property 
  set in Flask's g object

  :param token: token to verify
  """

    secret_key = current_app.config["JWT_SECRET_KEY"]

    g.jwt_claims = {}

    try:
        g.jwt_claims = jwt.decode(
            token,
            secret_key,
            algoritms=["HS256"],
            options={"verify_exp": False})
    except:
        return False

    return True


def generate_access_token(refresh_token, access_token):
    _refresh_token = RefreshToken.first(token=refresh_token)

    if _refresh_token is None or not verify_token(access_token):
        raise InvalidTokenError()

    if _refresh_token.revoked:
        raise RevokedTokenError()

    if _refresh_token.is_compromised(access_token):
        raise TokenCompromisedError()

    if not is_token_expired(g.jwt_claims["exp"]):
        raise AccessTokenNotExpiredError()

    new_access_token = generate_token(g.jwt_claims["user_id"])

    _refresh_token.mapped_token = new_access_token

    return new_access_token
