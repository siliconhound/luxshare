from flask import (jsonify, make_response, request, url_for, current_app,
                   flash, redirect, render_template, get_flashed_messages)
from sqlalchemy import or_
from datetime import datetime, timedelta
import jwt

from app import db
from app.models.user import User

from . import bp
from .utils import (generate_token, is_token_revoked, revoke_token,
                    verify_token, user_not_logged)

# TODO: Turn register and login routes into normal logins, so we can redirect
# TODO: If user has auth token redirect from /register and /login


@bp.route("/register", methods=["GET", "POST"])
@user_not_logged
def register_user():

  if request.method == "GET":
    return render_template("register.html", messages=get_flashed_messages())

  username = request.form["username"]
  email = request.form["email"]
  password = request.form["password"]

  #TODO: validate data
  user = User.first(username=username)

  if user is not None:
    flash(f"user {username} has already been registered")
    return redirect(url_for("register_user")), 422

  try:
    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
  except:
    flash("an error has ocurred, please try again")
    return redirect(url_for("register_user")), 500

  response = make_response(redirect("/"))

  response.set_cookie(
      "auth_token",
      generate_token(user.username),
      expires=datetime.utcnow() + timedelta(minutes=5),
      httponly=True)

  response.set_cookie(
      "refresh_token",
      generate_token(user.username, 3600 * 24 * 7),
      expires=datetime.utcnow() + timedelta(days=8),
      httponly=True)

  return response


@bp.route("/login", methods=["POST"])
@user_not_logged
def login():
  id = request.form["id"]
  password = request.form["password"]

  if not id:
    flash("no username or email provided")
    return redirect(url_for("login")), 422

  if not password:
    flash("no password provided")
    return redirect(url_for("login")), 422

  user = User.query.filter(or_(User.username == id, User.email == id)).first()

  if user is None:
    flash(f"no user with username or email {id} found")
    return redirect(url_for("login")), 404

  if not user.check_password(password):
    flash("invalid credentials")
    return redirect("/"), 401

  flash("login successful")
  response = make_response(redirect("/"))

  response.set_cookie(
      "auth_token",
      generate_token(user.username),
      expires=datetime.utcnow() + timedelta(days=1),
      httponly=True)

  response.set_cookie(
      "refresh_token",
      generate_token(user.username, 3600 * 24 * 7),
      expires=datetime.utcnow() + timedelta(minutes=5),
      httponly=True)

  return response


@bp.route("/logout", methods=["POST"])
def logout():
  if "refresh_token" in request.cookies:
    revoke_token(request.cookies["refresh_token"])

  response = make_response(jsonify({"message": "logout successful"}))

  response.set_cookie("auth_token", "", httponly=True)
  response.set_cookie("refresh_token", "", httponly=True)

  return response