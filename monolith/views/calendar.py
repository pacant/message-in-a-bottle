from flask import Blueprint
from flask_login.utils import login_required
from monolith.database import Message, User, db
from flask.templating import render_template
from flask_login import current_user

calendar = Blueprint('calendar', __name__)


@ calendar.route("/calendar/sent")
@ login_required
def calendar_sent():
    msgs_sent = db.session.query(Message, User).filter(
        Message.id_receiver == User.id).filter(
            Message.id_sender == current_user.id).filter(Message.delivered).all()

    return render_template("calendar.html", msgs_sent=msgs_sent)


@ calendar.route("/calendar/received")
@ login_required
def calendar_received():
    msgs_rcv = db.session.query(Message, User).filter(
        Message.id_sender == User.id).filter(
            Message.id_receiver == current_user.id).filter(Message.delivered).filter(Message.deleted.is_(False)).all()

    return render_template("calendar.html", msgs_rcv=msgs_rcv)
