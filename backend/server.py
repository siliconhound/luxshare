from app import create_app

app = create_app()

from app import db
from app.models.comment import Comment
from app.models.hashtag import Hashtag
from app.models.picture import Picture
from app.models.post import Post
from app.models.user import User



@app.shell_context_processor
def make_shell_context():
  return {
    "db": db,
    "Post": Post,
    "User": User,
    "Comment": Comment,
    "Hashtag": Hashtag,
    "Picture": Picture
  }
