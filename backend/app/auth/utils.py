import jwt
import re
from flask import current_app, request, jsonify
from datetime import datetime, timedelta
from app.models.blacklist_token import BlacklistToken
from app import db


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

  secret_key = current_app.config["JWT_SECRET_KEY"]
  if is_token_revoked(token):
    return False

  try:
    jwt.decode(token, secret_key, algoritms=["HS256"])
  except:
    return False

  return True


def revoke_token(token):
  if not is_token_revoked(token):
    token = BlacklistToken(token=token)
    db.session.add(token)
    db.session.commit()


def is_email(string):
  match = re.match(r"[^@]+@[^@]+\.[^@]+", string)
  return match is not None


def login_required(f):

  def f_wrapper(*args, **kwargs):
    if "auth_token" in request.cookies and verify_token(
        request.cookies.get("auth_token")):
      return f(*args, **kwargs)
    
    return jsonify({"message": "please log in"}), 401
  
  return f_wrapper
