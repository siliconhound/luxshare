from flask import Blueprint

bp = Blueprint("site", __name__, template_folder="templates")

from . import routes