from app import db
from .common import BaseMixin
from .tables import hashtag_post

class Hashtag(BaseMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(50), index=True, unique=True)
  posts = db.relationship("Post", secondary=hashtag_post, backref="hashtags", lazy="dynamic")

  def __repr__(self):
    return "<Hashtag {}>".format(self.title)
