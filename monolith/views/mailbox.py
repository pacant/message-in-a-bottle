from flask import Blueprint, request
from flask.templating import render_template
from flask_login import current_user
from monolith.database import User, Message, db

mailbox = Blueprint('mailbox', __name__)


@mailbox.route('/mailbox/sent', methods=['GET'])
def see_sent_messages():
    if request.method == 'GET':
        msgs_sent = db.session.query(Message, User).filter(
            Message.id_receiver == User.id).filter(
                Message.id_sender == current_user.id).filter(Message.draft.is_(False)).all()
        return render_template('msgs_sent.html', msgs_sent=msgs_sent)
    else:
        return render_template('msgs_sent.html')


@mailbox.route('/mailbox/received', methods=['GET'])
def see_received_messages():
    if request.method == 'GET':
        msgs_rcv = db.session.query(Message, User).filter(
            Message.id_sender == User.id).filter(
                Message.id_receiver == current_user.id).filter(Message.delivered).all()
        return render_template('msgs_rcv.html', msgs_rcv=msgs_rcv)
    else:
        return render_template('msgs_rcv.html')


@mailbox.route('/mailbox/draft', methods=['GET'])
def see_draft_messages():
    if request.method == 'GET':
        draft_msgs = db.session.query(Message, User).filter(Message.id_receiver == User.id).filter(
            Message.id_sender == current_user.id).filter(Message.draft)
        draft_msgs = draft_msgs.all()
        return render_template('msgs_draft.html', draft_msgs=draft_msgs)
    else:
        return render_template('msgs_draft.html')
