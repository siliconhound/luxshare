from flask import Blueprint

bp = Blueprint("token", __name__)

from . import routes