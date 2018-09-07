from flask import jsonify, make_response, request, url_for, current_app
from sqlalchemy import or_
from datetime import datetime, timedelta
import jwt

from app import db
from app.models.user import User

from . import bp
from .utils import generate_token, is_token_revoked, revoke_token, verify_token

# TODO: Turn register and login routes into normal logins, so we can redirect
# TODO: If user has auth token redirect from /register and /login


@bp.route("/register", methods=["POST"])
def register():
  if "auth_token" in request.cookies and verify_token(
      request.cookies.get("auth_token")):
    return jsonify({"message": "user is logged in"}), 400

  data = request.get_json() or {}

  if not data:
    return jsonify({"message": "no data provided"}), 400

  #TODO: validate data
  user = User.first(username=data["username"])

  if user is not None:
    return jsonify({"message": "user has already been registered"}), 422

  try:
    user = User(**data)
    db.session.add(user)
    db.session.commit()
  except:
    return jsonify({"message": "an error has ocurred, please try again"}), 500

  response = make_response(
      jsonify({
          "message": "user has been registered successfully",
      }))

  response.set_cookie(
      "auth_token",
      generate_token(user.username),
      expires=datetime.utcnow() + timedelta(days=1),
      httponly=True)

  return response


@bp.route("/login", methods=["POST"])
def login():
  if "auth_token" in request.cookies and verify_token(
      request.cookies.get("auth_token")):
    return jsonify({"message": "already logged in"}), 400

  data = request.get_json() or {}

  if not data:
    return jsonify({"message": "no data provided"}), 400

  if "id" not in data:
    return jsonify({"message": "no username or email provided"}), 422

  user = User.query.filter(
      or_(User.username == data["id"], User.email == data["id"])).first()

  if user is None:
    return jsonify({"message": "user not found"}), 404

  if not user.check_password(data["password"]):
    return jsonify({"message": "invalid credentials"}), 401

  response = make_response(jsonify({"message": "login successful"}))

  response.set_cookie(
      "auth_token",
      generate_token(user.username),
      expires=datetime.utcnow() + timedelta(days=1),
      httponly=True)

  return response


@bp.route("/logout", methods=["POST"])
def logout():
  if "auth_token" in request.cookies:
    auth_token = request.cookies.get("auth_token")
  else:
    return jsonify({"message": "already logged out"}), 400

  try:
    secret_key = current_app.config["JWT_SECRET_KEY"]
    jwt.decode(auth_token, secret_key, algorithms=["HS256"])
  except jwt.InvalidTokenError:
    return jsonify({"message": "invalid token"}), 400

  revoke_token(auth_token)

  response = make_response(jsonify({"message": "logged out"}))
  response.set_cookie("auth_token", "", httponly=True)

  return response