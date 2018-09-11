from app import db
from .common import DateAudit, BaseMixin

class Picture(BaseMixin, DateAudit, db.Model):
  __tablename__ = "picture"
  id = db.Column(db.Integer, primary_key=True)
  public_id = db.Column(db.String(256), index=True, unique=True)
  path = db.Column(db.Text)
  post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
  user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
  user = db.relationship("User", back_populates="avatar")

  def __repr__(self):
    return "<Picture {}>".format(self.id)
