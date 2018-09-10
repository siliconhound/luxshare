import jwt
import re
from functools import wraps
from flask import current_app, request, jsonify, make_response, redirect, g
from datetime import datetime, timedelta
from app.models.refresh_token import RefreshToken
from app.token.errors import TokenCompromisedError
from app import db
from uuid import uuid4

INVALID_TOKEN = 0
EXPIRED_TOKEN = 1
VALID_TOKEN = 2

def generate_csrf_token():
  return str(uuid4())

def generate_token(user_id, expires_in=60):
  """Generate a JWT token

  :param user_id the user that will own the token
  :param expires_in expiration time in seconds
  """
  secret_key = current_app.config["JWT_SECRET_KEY"]
  return jwt.encode(
      {
          "user_id": user_id,
          "iat": datetime.utcnow(),
          "exp": datetime.utcnow() + timedelta(seconds=expires_in)
      },
      secret_key,
      algorithm="HS256").decode("utf-8")

def is_token_expired(exp):
  return datetime.strptime(exp, "%Y-%m-%d %H:%M:%S.%f") < datetime.utcnow()

def verify_token(token):
  """Token verification

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


def is_email(string):
  match = re.match(r"[^@]+@[^@]+\.[^@]+", string)
  return match is not None


# TODO: change method
def login_required(f):

  def f_wrapper(*args, **kwargs):
    if "auth_token" in request.cookies and verify_token(
        request.cookies.get("auth_token")):
      return f(*args, **kwargs)

    return jsonify({"message": "please log in"}), 401

  return f_wrapper


def user_not_logged(f):
  """decorator to redirect if user is already logged in"""

  @wraps(f)
  def f_wrapper(*args, **kwargs):
    if "access_token" in request.cookies:
      access_token = request.cookies["access_token"]

      if verify_token(access_token):
        return f(*args, **kwargs)

      if not is_token_expired(g.jwt_claims["exp"]):
        return redirect("/")

      if "refresh_token" in request.cookies:
        refresh_token = request.cookies["refresh_token"]

        try:
          token = RefreshToken.generate_access_token(refresh_token,
                                                      access_token)
          db.session.commit()
          response = make_response(redirect("/"))
          response.set_cookie("access_token", token, httponly=True)
          return response
        except TokenCompromisedError:
          db.session.commit()
        except:
          return f(*args, **kwargs)

    return f(*args, **kwargs)

  return f_wrapper
