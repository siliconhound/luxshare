from app.models.refresh_token import RefreshToken
from app import db
from datetime import datetime, timedelta
from .utils import generate_token
from uuid import uuid4

def set_session_tokens(response, username):
  """Sets session tokens (access and refresh) in cookies

  :param response: response object
  :param username: user username to attach to jwt
  """

  user_has_tokens = RefreshToken.query.filter(
      RefreshToken.user_id == username,
      RefreshToken.expires_at > datetime.utcnow(),
      RefreshToken.revoked == False).first()

  if user_has_tokens is not None:
    RefreshToken.revoke_user_tokens(user_id=username)
    db.session.commit()
    return

  access_token = generate_token(username)
  
  refresh_token = RefreshToken(token=str(uuid4()), mapped_token=access_token)
  db.session.add(refresh_token)
  db.session.commit()

  response.set_cookie("access_token", access_token, httponly=True)
  response.set_cookie(
      "refresh_token",
      refresh_token.token,
      expires=datetime.utcnow() + timedelta(days=7),
      httponly=True)
