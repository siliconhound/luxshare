from . import bp
from flask import render_template, make_response
from app.auth.csrf import generate_csrf_token, set_csrf_token_cookie

@bp.route("/")
def index():

    csrf_token = generate_csrf_token()
    response = make_response(render_template("app.html", csrf_token=csrf_token))
    set_csrf_token_cookie(response, csrf_token)
    return response