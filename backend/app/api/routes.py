from app import db
from . import bp

@bp.route("/user/<str:username>")
def get_user(username):
  pass


@bp.route("/user/<str:username>", methods=["PATCH"])
def edit_user(username):
  pass


@bp.route("/user/<str:username>/posts")
def get_user_posts(username):
  pass


@bp.route("/user/<str:username>/comments")
def get_user_comments(username):
  pass
