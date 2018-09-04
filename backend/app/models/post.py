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

  def __repr__(self):
    return "<Post {}>".format(self.title)
