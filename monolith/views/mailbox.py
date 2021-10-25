from flask import Blueprint, request, jsonify, session
from flask.templating import render_template
from flask_login import current_user
from monolith.database import Message, db

mailbox = Blueprint('mailbox', __name__)

@mailbox.route('/mailbox/sent', methods = ['GET'])
def see_sent_messages(): 
    if request.method == 'GET':
        msgs_sent = db.session.query(Message).filter(Message.sender==current_user.id)
        return render_template('msgs_sent.html', msgs_sent=msgs_sent)
    else:
        return render_template('msgs_sent.html')


@mailbox.route('/mailbox/received', methods = ['GET'])
def see_received_messages():
    if request.method == 'GET':
        msgs_rcv = db.session.query(Message).filter(Message.receiver==current_user.id)
        return render_template('msgs_rcv.html', msgs_rcv=msgs_rcv)
    else:
        return render_template('msgs_rcv.html')
