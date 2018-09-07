from app import db
from flask import url_for
from .common import BaseMixin

class Hashtag(BaseMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(50), index=True, unique=True)

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
