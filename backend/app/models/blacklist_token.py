from app import db
from .common import BaseMixin
from datetime import datetime

class BlacklistToken(BaseMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  token = db.Column(db.String(500), unique=True, index=True)
  revoked_on = db.Column(db.DateTime, default=datetime.utcnow())

  def __repr__(self):
    return "<Token {}>".format(self.token)
