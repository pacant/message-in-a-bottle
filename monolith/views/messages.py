from flask import Blueprint, request, redirect
from monolith.database import Message, db, User
from dateutil import parser
from flask.templating import render_template
from monolith.background import send_message
from monolith.auth import current_user
messages = Blueprint('messages', __name__)


@messages.route('/message/send', methods=['GET', 'POST'])
def sendMessage():
    if current_user is not None and hasattr(current_user, 'id'):

        if request.method == 'POST':
            date = parser.parse(request.form['date']+'+0200')
            data = request.form
            id_message = save_message(data)
            result = send_message.apply_async((id_message,), eta=date)
            return render_template("send_message.html", message_ok=True)
        else:
            return render_template("send_message.html")

    else:
        return redirect('/')


@messages.route('/draft', methods=['POST'])
def draft():
    data = request.form
    save_message(data)
    return render_template("send_message.html", draft_ok=True)


def save_message(data):

    message = Message()
    message.text = data['text']
    id_receiver = db.session.query(User).filter(
        User.email == data['receiver']).first().id
    message.id_receiver = id_receiver
    message.id_sender = current_user.id
    message.draft = True if 'draft' in data else False

    db.session.add(message)
    db.session.commit()

    return message.id
