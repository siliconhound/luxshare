from app import db
from flask import url_for
from .common import BaseMixin
from .tables import hashtag_post

class Hashtag(BaseMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(50), index=True, unique=True)
  posts = db.relationship("Post", secondary=hashtag_post, backref="hashtags", lazy="dynamic")

  ATTR_FIELDS = ["title"]

  def __repr__(self):
    return "<Hashtag {}>".format(self.title)

  def to_dict(self):
    return {
      "title": self.title,
      "audit_dates": self.audit_dates(),
      "_links": {
        "posts": url_for("hashtag_posts", hashtag=self.title)
      }
    }
