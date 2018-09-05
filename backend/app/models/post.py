from app import db
from .common import BaseMixin, DateAudit

class Post(BaseMixin, DateAudit, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  public_id = db.Column(db.String(256), index=True, unique=True)
  title = db.Column(db.String(256), index=True)
  pictures = db.relationship("Picture", backref="post", lazy="dynamic")
  description = db.Column(db.String(256), nullable=True)
  user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
  comments = db.relationship("Comment", backref="post", lazy="dynamic")
  tagged_users = db.relationship("User", backref="posts_tagged", lazy="dynamic")

  ATTR_FIELDS = ["tile", "description"]

  def __repr__(self):
    return "<Post {}>".format(self.title)

  def to_dict(self):
    return {
      "public_id": self.public_id,
      "title": self.title,
      "description": self.description,
      "audit_dates": self.audit_dates(),
      "post_author": self.author,
      "_links": {
        "pictures": url_for("post_pictures", public_id=self.public_id),
        "comments": url_for("post_comments", public_id=self.public_id),
        "tagged_users": url_for("post_tagged_users", public_id=self.public_id),
      }
    }
