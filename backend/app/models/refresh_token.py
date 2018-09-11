from datetime import datetime, timedelta

from flask import g

from app import db
from app.models.common import BaseMixin
from app.token.errors import (AccessTokenNotExpiredError, InvalidTokenError,
                              RevokedTokenError, TokenCompromisedError)
from app.token.utils import generate_token, is_token_expired, verify_token


class RefreshToken(db.Model, BaseMixin):
  token = db.Column(db.String(256), primary_key=True)
  issued_at = db.Column(db.DateTime(), default=datetime.utcnow())
  expires_at = db.Column(
      db.DateTime(), default=datetime.utcnow() + timedelta(days=7))
  mapped_token = db.Column(db.String(512))
  revoked = db.Column(db.Boolean(), default=False)

  def __repr__(self):
    return f"<Token {self.token}>"

  def check_user(self, user_id):
    return self.user_id == user_id

  def has_expired(self):
    return self.expires_at < datetime.utcnow()

  def is_valid(self):
    return not (self.has_expired() or self.revoked)

  def is_compromised(self, access_token):
    return not (verify_token(access_token) and
                self.mapped_token == access_token)

  @classmethod
  def is_token_valid(cls, token):
    _token = cls.first(token=token)

    return _token is not None and _token.is_valid()

  @classmethod
  def revoke_token(cls, token="", instance=None):
    _token = None

    if instance is not None:
      _token = instance
    else:
      _token = cls.first(token=token)

    if _token is not None and not _token.is_valid():
      _token.revoked = True
      return True
    return False

  @classmethod
  def revoke_user_tokens(cls, refresh_token="", user_id=""):
    user = user_id

    if refresh_token:
      token = cls.first(token=refresh_token)

      if token is None:
        return

      user = token.user_id
    elif user_id:
      user = user_id

    cls.update().where(cls.c.user_id == user,
                       cls.c.expires_at > datetime.utcnow(),
                       cls.c.revoked == False).values(revoked=True)

  @classmethod
  def generate_access_token(cls, refresh_token, access_token):
    _refresh_token = cls.first(token=refresh_token)

    if _refresh_token is None:
      raise InvalidTokenError()

    if _refresh_token.revoked:
      raise RevokedTokenError()

    if _refresh_token.is_compromised(access_token):
      raise TokenCompromisedError()

    if is_token_expired(g.jwt_claims["exp"]):
      raise AccessTokenNotExpiredError()

    new_access_token = generate_token(g.jwt_claims["user_id"])

    _refresh_token.mapped_token = new_access_token

    return new_access_token
