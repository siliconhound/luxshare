from datetime import datetime, timedelta
from uuid import uuid4

import jwt
from flask import (current_app, flash, g, get_flashed_messages, jsonify,
                   make_response, redirect, render_template, request, url_for)
from sqlalchemy import or_

from app import db
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.token.utils import generate_token, set_session_tokens

from . import bp
from .utils import login_required, user_not_logged, verify_token
from .csrf import generate_csrf_token, set_csrf_token


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
  set_session_tokens(response, user.username)
  set_csrf_token(response)
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

  csrf_token = generate_csrf_token()
  access_token = generate_token(user.username)
  refresh_token = RefreshToken(
      token=str(uuid4()).replace("-", ""), mapped_token=access_token)
  db.session.add(refresh_token)
  db.session.commit()

  response.set_cookie("access_token", access_token, httponly=True)
  response.set_cookie(
      "refresh_token",
      refresh_token,
      expires=datetime.utcnow() + timedelta(days=7),
      httponly=True)
  response.set_cookie("x-csrf-token", csrf_token, httponly=True)
  response.headers["x-csrf-token"] = csrf_token

  return response


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
  RefreshToken.revoke_user_tokens(g.jwt_claims["user_id"])
  response = make_response(jsonify({"message": "logout successful"}))

  response.set_cookie("auth_token", "", httponly=True)
  response.set_cookie("refresh_token", "", httponly=True)
  response.set_cookie("x-csrf-token", "", httponly=True)

  return response
