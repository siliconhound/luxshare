from datetime import datetime, timedelta
from uuid import uuid4

from flask import request


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


def set_csrf_token(response):
  """Sets CSRF token to header and cookie

  :param response: response object
  """

  csrf_token = generate_csrf_token()

  response.set_cookie(
      "x-csrf-token",
      csrf_token,
      httponly=True,
      expires=datetime.utcnow() + timedelta(days=7))

  response.headers["x-csrf-token"] = csrf_token
