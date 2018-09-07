import jwt
import re
from flask import current_app
from datetime import datetime, timedelta
from app.models.blacklist_token import BlacklistToken


def generate_token(user_id, expires_in=3600):
  """Generate a JWT token

  :param user_id the user that will own the token
  :param expires_in expiration time in seconds
  """
  secret_key = current_app.config["JWT_SECRET_KEY"]
  return jwt.encode(
      {
          "user_id": user_id,
          "exp": datetime.utcnow() + timedelta(seconds=expires_in)
      },
      secret_key,
      algorithm="HS256").decode("utf-8")


def is_token_revoked(token):
  """Check if token has been rovoked

  :param token: token to check
  """
  token = BlacklistToken.first(token=token)

  if token is None:
    return False
  return True


def verify_token(token):
  """Token verification

  :param token: token to verify
  """

  jwt_claims = {}
  secret_key = current_app.config["JWT_SECRET_KEY"]
  if is_token_revoked(token):
    return False

  try:
    jwt_claims = jwt.decode(token, secret_key, algoritms=["HS256"])
  except:
    return False

  return True


def is_email(string):
  match = re.match(r"[^@]+@[^@]+\.[^@]+", string)
  return match is not None
