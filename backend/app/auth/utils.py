import re
from functools import wraps

from flask import g, jsonify, make_response, redirect, request

from app import db
from app.models.refresh_token import RefreshToken
from app.token.errors import TokenCompromisedError
from app.token.utils import is_token_expired, verify_token

from .csrf import validate_csrf_token


def is_email(string):
  match = re.match(r"[^@]+@[^@]+\.[^@]+", string)
  return match is not None


def login_required(f):
  """decorator for login required routes"""

  @wraps(f)
  def f_wrapper(*args, **kwargs):
    if not validate_csrf_token():
      return jsonify({"message": "request compromised"}), 401
    if "access_token" not in request.cookies:
      return jsonify({"message": "invalid credentials"}), 401

    access_token = request.cookies["access_token"]

    if not (access_token and verify_token(access_token)):
      return jsonify({"message": "invalid credentials"}), 401

    if is_token_expired(g.jwt_claims["exp"]):
      return jsonify({"message": "expired access token"}), 401

    return f(*args, **kwargs)

  return f_wrapper


def user_not_logged(f):
  """decorator to redirect if user is already logged in"""

  @wraps(f)
  def f_wrapper(*args, **kwargs):
    if "access_token" in request.cookies:
      access_token = request.cookies["access_token"]

      if not verify_token(access_token):
        return f(*args, **kwargs)

      if not is_token_expired(g.jwt_claims["exp"]):
        return redirect("/")

      if "refresh_token" in request.cookies:
        refresh_token = request.cookies["refresh_token"]
        token = ""
        try:
          token = RefreshToken.generate_access_token(refresh_token,
                                                     access_token)
          db.session.commit()
        except TokenCompromisedError:
          RefreshToken.revoke_user_tokens(refresh_token)
          db.session.commit()
        except:
          return f(*args, **kwargs)

        response = make_response(redirect("/"))
        response.set_cookie("access_token", token, httponly=True)
        return response

    return f(*args, **kwargs)

  return f_wrapper
