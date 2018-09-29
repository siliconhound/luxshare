from flask import Blueprint
from uuid import uuid4
bp = Blueprint("token", __name__)

from . import routes
from app import tok_schema, db
from app.models.refresh_token import RefreshToken
from app.token_schema import InvalidRefreshTokenError


@tok_schema.verify_refresh_token
def verify_refresh_token(refresh_token):
    token = RefreshToken.first(token=refresh_token)
    if token is None:
        return False

    return token.is_valid()


@tok_schema.revoke_user_refresh_tokens
def revoke_user_refresh_tokens(user_id):
    RefreshToken.revoke_user_tokens(user_id)


@tok_schema.create_refresh_token
def create_refresh_token(user_id, access_token):
    token = RefreshToken(
        token=str(uuid4()), user_id=user_id, mapped_token=access_token)
    
    db.session.add(token)
    db.session.commit()

    return token.token

@tok_schema.compromised_tokens
def compromised_tokens(refresh_token, access_token):
    token = RefreshToken.first(token=refresh_token)
    if token is None:
        return False

    return token.is_compromised(access_token)

@tok_schema.after_new_access_token_created
def after_new_access_token_created(new_access_token, refresh_token):
    token = RefreshToken.first(token=refresh_token)
    if token is None:
        raise InvalidRefreshTokenError
    
    token.mapped_token = new_access_token
    db.session.commit()    