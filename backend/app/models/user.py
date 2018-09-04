from .common import BaseMixin, DateAudit
from .tables import followers
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(BaseMixin, DateAudit):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), index=True, unique=True)
  email = db.Column(db.String(256), index=True, unique=True)
  password_hash = db.Column(db.String(128))
  posts = db.relationship("Post", backref="author", lazy="dynamic")
  comments = db.relationship("Comment", backref="author", lazy="dynamic")
  bio = db.Column(db.String(256))
  followed = db.relationship(
      "User",
      secondary=followers,
      primaryjoin=(followers.c.follower_id == id),
      secondaryjoin=(followers.c.follwed_id == id),
      backref=db.backref("followers", lazy="dynamic"), lazy="dynamic")

  ATTR_FIELDS = ["username", "email", "bio"]

  def __repr__(self):
    return "<User {}>".format(self.username)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  def avatar(self, size):
    digest = md5(self.email.lower().encode('utf-8')).hexdigest()
    return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
      digest, size)

  def follow(self, user):
    if not self.is_following(user):
      self.followed.append(user)

  def unfollow(self, user):
    if self.is_following(user):
      self.followed.remove(user)

  def is_following(self, user):
    return self.followed.filter(
      followers.c.followed_id == user.id).count() > 0
