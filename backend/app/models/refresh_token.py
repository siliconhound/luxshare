from datetime import datetime, timedelta

from app import db
from app.models.common import BaseMixin
from sqlalchemy import and_


class RefreshToken(db.Model, BaseMixin):
    __tablename__ = "refresh_token"
    token = db.Column(db.String(256), primary_key=True)
    issued_at = db.Column(db.DateTime(), default=datetime.utcnow())
    expires_at = db.Column(
        db.DateTime(), default=datetime.utcnow() + timedelta(days=7))
    mapped_token = db.Column(db.String(512))
    user_id = db.Column(db.String(256))
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
        return self.mapped_token != access_token

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

        if _token is not None and _token.is_valid():
            _token.revoked = True

    @classmethod
    def revoke_user_tokens(cls, user_id="", refresh_token=""):
        user = user_id

        if refresh_token:
            token = cls.first(token=refresh_token)

            if token is None:
                return

            user = token.user_id
        elif user_id:
            user = user_id
        table = cls.__table__
        table.update().where(and_(table.c.user_id == user,
                           table.c.expires_at > datetime.utcnow(),
                           table.c.revoked == False)).values(revoked=True)
