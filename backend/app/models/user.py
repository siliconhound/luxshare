from .common import BaseMixin, DateAudit
from .tables import followers
from app import db, photos
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(BaseMixin, DateAudit, db.Model):
  __tablename__ = "user"
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), index=True, unique=True)
  email = db.Column(db.String(256), index=True, unique=True)
  password_hash = db.Column(db.String(128))
  avatar = db.relationship("Picture", uselist=False, back_populates="user")
  posts = db.relationship("Post", backref="author", lazy="dynamic")
  comments = db.relationship("Comment", backref="author", lazy="dynamic")
  bio = db.Column(db.String(256))
  followed = db.relationship(
      "User",
      secondary=followers,
      primaryjoin=(followers.c.follower_id == id),
      secondaryjoin=(followers.c.followed_id == id),
      backref=db.backref("followers", lazy="dynamic"), lazy="dynamic")

  ATTR_FIELDS = ["username", "email", "bio"]

  def __repr__(self):
    return "<User {}>".format(self.username)

  @property
  def password(self):
    raise AttributeError("password is not a readable attribute")
  
  @password.setter
  def password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  def get_avatar(self):
    if self.avatar is not None:
      return photos.url(self.avatar.path)

    digest = md5(self.email.lower().encode('utf-8')).hexdigest()
    return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
      digest, 128)

  def follow(self, user):
    if not self.is_following(user):
      self.followed.append(user)

  def unfollow(self, user):
    if self.is_following(user):
      self.followed.remove(user)

  def is_following(self, user):
    return self.followed.filter(
      followers.c.followed_id == user.id).count() > 0

  def to_dict(self):
    return {
      "username": self.username,
      "email": self.email,
      "bio": self.bio,
      "avatar": self.get_avatar(),
      "audit_dates": self.audit_dates(),
      "_links": {
        "posts": url_for("user_posts", username=self.username),
        "comments": url_for("user_comments", username=self.username),
        "followers": url_for("user_followers", username=self.username),
        "following": url_for("user_following", username=self.username)
      }
    }

