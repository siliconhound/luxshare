from app import db
from .common import BaseMixin, DateAudit

class Comment(BaseMixin, DateAudit, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  public_id = db.Column(db.String(256), index=True, unique=True)
  body = db.Column(db.String(256))
  user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

  ATTR_FIELDS = ["body"]

  def __repr__(self):
    return "<Comment {}>".format(self.body)

  def to_dict(self):
    return {
      "public_id": self.public_id,
      "body": self.body,
      "author_username": self.author.username,
      "audit_dates": self.audit_dates()
    }

