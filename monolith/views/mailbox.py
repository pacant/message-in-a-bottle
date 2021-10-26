from operator import and_
from flask import Blueprint, request, jsonify, session
from flask.templating import render_template
from flask_login import current_user
from monolith.database import User, Message, db
from sqlalchemy import and_

mailbox = Blueprint('mailbox', __name__)

@mailbox.route('/mailbox/sent', methods = ['GET'])
def see_sent_messages(): 
    if request.method == 'GET':
        msgs_sent = db.session.query(Message, User).filter(Message.id_sender==User.id).filter(Message.id_sender==current_user.id).all()
        return render_template('msgs_sent.html', msgs_sent=msgs_sent)
    else:
        return render_template('msgs_sent.html')


@mailbox.route('/mailbox/received', methods = ['GET'])
def see_received_messages():
    if request.method == 'GET':
        msgs_rcv = db.session.query(Message, User).filter(Message.id_receiver==User.id).filter(Message.id_receiver==current_user.id).all()
        return render_template('msgs_rcv.html', msgs_rcv=msgs_rcv)
    else:
        return render_template('msgs_rcv.html')
