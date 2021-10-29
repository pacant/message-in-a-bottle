from flask import Blueprint, request, redirect, abort
from sqlalchemy.orm import query
from monolith.database import Message, db, User
from dateutil import parser
from flask.templating import render_template
from flask_login import current_user
from monolith.background import send_message as send_message_task

messages = Blueprint('messages', __name__)


@messages.route('/message/send/<id_message>', methods=['GET', 'POST'])
def send_draft(id_message):
    if current_user is not None and hasattr(current_user, 'id'):

        if request.method == 'POST':
            send_message_async(request.form)
            db.session.query(Message).filter(Message.id == id_message).delete()
            db.session.commit()
            return render_template("send_message.html", message_ok=True)
        else:
            message = db.session.query(Message).filter(Message.id == id_message).first()
            receiver = db.session.query(User).filter(User.id == message.id_receiver).first().email
            date = message.date_delivery.isoformat()
            text = message.text
            form = dict(recipient=receiver, text=text, date=date, message_id=message.id)
            return render_template("send_message.html", form=form)

    else:
        return redirect('/message/send')


@ messages.route('/message/send', methods=['GET', 'POST'])
def send_message():
    if current_user is not None and hasattr(current_user, 'id'):

        if request.method == 'POST':
            send_message_async(request.form)
            return render_template("send_message.html", form=dict(), message_ok=True)
        else:
            # landing from the recipients page, we want to populate the field with the chosen one
            recipient_message = request.args.get('recipient')
            recipient = recipient_message if recipient_message is not None else ''
            form = dict(recipient=recipient)
            return render_template("send_message.html", form = form)

    else:
        return redirect('/')


@ messages.route('/draft', methods=['POST'])
def draft():
    data = request.form
    save_message(data)
    return redirect('/mailbox/draft')


@ messages.route("/message/recipients", methods=["GET", "POST"])
def chooseRecipient():
    if request.method == "GET":
        email = current_user.email
        recipients = db.session.query(User).filter(User.email != email)
        return render_template("recipients.html", recipients=recipients)
    if request.method == "POST":
        recipient = request.form.get("recipient")
        return render_template("send_message.html", recipient=recipient)


@ messages.route('/message/<message_id>')
def viewMessage(message_id):
    if current_user is None or not hasattr(current_user, 'id'):
        return redirect('/')
    message = db.session.query(Message, User).filter(
        Message.id == int(message_id)
    ).join(User, Message.id_sender == User.id).first()

    if message is None or (int(message.Message.id_receiver) == current_user.id and not message.Message.delivered):
        abort(404)
    elif int(message.Message.id_sender) != current_user.id and int(message.Message.id_receiver) != current_user.id:
        abort(403)
    else:
        recipient = db.session.query(User).filter(
            User.id == message.Message.id_receiver
        ).first()
        return render_template("message.html",
                               sender=message.User,
                               recipient=recipient,
                               message=message.Message,
                               date='-')


def send_message_async(data):
    date = parser.parse(data['date'] + '+0200')
    id_message = save_message(data)
    send_message_task.apply_async((id_message,), eta=date)


def save_message(data):

    message = Message()
    message.text = data['text']
    id_receiver = db.session.query(User).filter(
        User.email == data['receiver']).first().id
    message.id_receiver = id_receiver
    message.id_sender = current_user.id
    message.draft = True if 'draft' in data else False
    message.date_delivery = parser.parse(data['date'] + '+0200')
    db.session.add(message)
    db.session.commit()

    return message.id
