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

  from app.api import bp as api_bp
  app.register_blueprint(api_bp)

  return app

from app import models
