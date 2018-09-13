from datetime import datetime, timedelta
from uuid import uuid4
from functools import wraps

from flask import request, jsonify


def generate_csrf_token():
  return str(uuid4())


def validate_csrf_token():
  """validate if x-csrf-token cookie and header are valid and equal"""

  if not ("x-csrf-token" in request.cookies and
          "x-csrf-token" in request.headers):
    return False

  cookie_csrf_token = request.cookies["x-csrf-token"]
  header_csrf_token = request.headers["x-csrf-token"]

  if not (cookie_csrf_token and header_csrf_token):
    return False

  if cookie_csrf_token != header_csrf_token:
    return False

  return True


def set_csrf_token_cookie(response, csrf_token):
  """Sets CSRF token to cookie

  :param response: response object
  """
  response.set_cookie(
      "x-csrf-token",
      csrf_token,
      httponly=True,
      expires=datetime.utcnow() + timedelta(days=7))

def csrf_token_required(f):

  @wraps(f)
  def f_wrapper(*args, **kwargs):

    if not validate_csrf_token():
      return jsonify({"message": "unauthorized"}), 401

    return f(*args, **kwargs)
  
  return f_wrapper
