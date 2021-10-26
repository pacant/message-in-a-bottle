from flask import Blueprint, request, redirect, abort
from monolith.database import Message, db, User
from dateutil import parser
from flask.globals import current_app
from flask.templating import render_template
from flask_login import current_user
from monolith.background import send_message
from monolith.auth import current_user

from monolith.database import User, db
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
            recipient_message = request.args.get('recipient')
            recipient = recipient_message if recipient_message is not None else ''
            return render_template("send_message.html", recipient=recipient)

    else:
        return redirect('/')


@messages.route('/draft', methods=['POST'])
def draft():
    data = request.form
    save_message(data)
    return redirect('/mailbox/draft')


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


@messages.route("/message/recipients", methods =["GET","POST"])
def chooseRecipient():
    if request.method == "GET":
        email = current_user.email
        recipients = db.session.query(User).filter(User.email != email)
        return render_template("recipients.html", recipients=recipients)
    if request.method == "POST":
        recipient = request.form.get("recipient")
        return render_template("send_message.html", recipient=recipient)


@messages.route('/message/<message_id>')
def viewMessage(message_id):
    if current_user is None or not hasattr(current_user, 'id'):
        return redirect('/')
    try:
        message = db.session.query(Message).filter(
            Message.id == int(message_id)
        ).join(User, Message.id_sender==User.id).first()
    except:
        abort(500)
    
    if message is None:
        abort(404)
    else:
        return render_template("message.html", sender=None, text=message, date=None)