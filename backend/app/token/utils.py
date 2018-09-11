from datetime import datetime, timedelta
from uuid import uuid4

import jwt
from flask import current_app, g

from app import db
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
  return datetime.strptime(exp, "%Y-%m-%d %H:%M:%S.%f") < datetime.utcnow()


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
        token, secret_key, algoritms=["HS256"], options={"verify_exp": False})
  except:
    return False

  return True


def set_session_tokens(response, username):
  """Sets session tokens (access and refresh) in cookies

  :param response: response object
  :param username: user username to attach to jwt
  """

  user_has_tokens = RefreshToken.query.where(
      RefreshToken.c.user_id == username,
      RefreshToken.c.expires_at > datetime.utcnow(),
      RefreshToken.c.revoked == False).first()
  if user_has_tokens is not None:
    RefreshToken.revoke_user_tokens(user_id=username)
    return

  access_token = generate_token(username)
  refresh_token = RefreshToken(token=str(uuid4()), mapped_token=access_token)
  db.session.add(refresh_token)
  db.session.commit()

  response.set_cookie("access_token", access_token, httponly=True)
  response.set_cookie(
      "refresh_token",
      refresh_token.token,
      expires=datetime.utcnow() + timedelta(days=7),
      httponly=True)
