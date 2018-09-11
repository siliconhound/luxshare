from config import Config
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, IMAGES

db = SQLAlchemy()
migrate = Migrate()
cors = CORS(resources={r"/api/*": {"origins": "*"}})
photos = UploadSet('photos', IMAGES)


def create_app(config_class=Config):
  app = Flask(__name__)
  app.config.from_object(config_class)

  db.init_app(app)
  migrate.init_app(app, db)
  cors.init_app(app)
  configure_uploads(app, photos)

  from app.token import bp as token_bp
  app.register_blueprint(token_bp, url_prefix="/token")

  from app.auth import bp as auth_bp
  app.register_blueprint(auth_bp, url_prefix="/auth")

  from app.site import bp as site_bp
  app.register_blueprint(site_bp)

  return app


from app import models
