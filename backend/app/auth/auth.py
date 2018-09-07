from flask import jsonify, make_response, request, url_for
from sqlalchemy import or_

from app import db
from app.models.user import User

from . import bp
from .utils import generate_token, is_email


# TODO: Turn register and login routes into normal logins, so we can redirect
@bp.route("/register", methods=["POST"])
def register():
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
      "auth_token", generate_token(user.username), httponly=True)

  return response


@bp.route("/login", methods=["POST"])
def login():
  data = request.get_json() or {}

  if not data:
    return jsonify({"message": "no data provided"}), 400

  if "id" not in data:
    return jsonify({"message": "no username or email provided"}), 422

  user = User.query.filter(
      or_(User.username == data["id"],
          User.email == data["id"])).first()

  if user is None:
    return jsonify({"message": "user not found"}), 404

  if not user.check_password(data["password"]):
    return jsonify({"message": "invalid credentials"}), 401

  response = make_response(jsonify({"message": "login successful"}))

  response.set_cookie(
      "auth_token", generate_token(user.username), httponly=True)

  return response


@bp.route("/logout", methods=["POST"])
def logout():
  pass


@bp.route("/tokens", methods=["POST"])
def refresh_token():
  pass


@bp.route("/tokens", methods=["DELETE"])
def revoke_refresh_token():
  pass
