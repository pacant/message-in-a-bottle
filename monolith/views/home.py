from flask import Blueprint, render_template

from flask_login import current_user

home = Blueprint('home', __name__)


@home.route('/', methods=["GET"])
def index():
    ''' GET: get the homepage'''
    if current_user is not None and hasattr(current_user, 'id'):
        welcome = "Logged In!"
    else:
        welcome = None
    return render_template("index.html", welcome=welcome)
