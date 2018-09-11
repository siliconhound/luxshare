from flask import (flash, g, get_flashed_messages, jsonify,
                   make_response, redirect, render_template, request, url_for)
from sqlalchemy import or_

from app import db
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.token.common import set_session_tokens

from . import bp
from .utils import login_required, user_not_logged 
from .csrf import csrf_token_required

@bp.route("/register", methods=["GET", "POST"])
@user_not_logged
def register_user():

  if request.method == "GET":
    return render_template("register.html", messages=get_flashed_messages())

  username = request.form["username"]
  email = request.form["email"]
  password = request.form["password"]
  confirm_password = request.form["confirm_password"]

  #TODO: validate data
  user_username = User.first(username=username)
  user_email = User.first(email=email)

  if user_username is not None:
    flash(f"{username} has already been registered")
    return redirect(url_for("auth.register_user")), 422

  if user_email is not None:
    flash(f"{email} has already been registered")
    return redirect(url_for("auth.register_user")), 422
  
  if password != confirm_password:
    flash("passwords don't match")
    return redirect(url_for("auth.register_user")), 422

  try:
    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
  except:
    flash("an error has ocurred, please try again")
    return redirect(url_for("auth.register_user")), 500

  response = make_response(redirect("/"))
  set_session_tokens(response, user.username)
  return response


@bp.route("/login", methods=["POST", "GET"])
@user_not_logged
def login():
  if request.method == "GET":
    return render_template("login.html", messages=get_flashed_messages())

  id = request.form["id"]
  password = request.form["password"]

  if not id:
    flash("no username or email provided")
    return redirect(url_for("auth.login")), 422

  if not password:
    flash("no password provided")
    return redirect(url_for("auth.login")), 422

  user = User.query.filter(or_(User.username == id, User.email == id)).first()

  if user is None:
    flash(f"no user with username or email {id} found")
    return redirect(url_for("auth.login")), 404

  if not user.check_password(password):
    flash("invalid credentials")
    return redirect(url_for("auth.login")), 401

  response = make_response(redirect("/"))
  set_session_tokens(response, user.username)
  return response


@bp.route("/logout", methods=["POST"])
@csrf_token_required
@login_required
def logout():
  RefreshToken.revoke_user_tokens(g.jwt_claims["user_id"])
  db.session.commit()
  response = make_response(jsonify({"message": "logout successful"}))

  response.set_cookie("access_token", "", httponly=True)
  response.set_cookie("refresh_token", "", httponly=True)
  response.set_cookie("x-csrf-token", "", httponly=True)

  return response
