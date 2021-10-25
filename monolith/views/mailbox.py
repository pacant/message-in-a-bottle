from flask import Blueprint, request, jsonify, redirect
from flask.templating import render_template
from flask_login import current_user
from monolith.database import Message, db

mailbox = Blueprint('mailbox', __name__)

@mailbox.route('/mailbox/sent', methods = ['GET'])
def see_sent_messages(): 
    if request.method == 'GET':
        if current_user.is_authenticated:
            user_id = current_user.get_id()
            print("ID: " + str(current_user.id))
            sent_msgs = db.session.query(Message).filter(Message.sender==) 
            print(sent_msgs)
        return render_template('mailbox.html', sent_msgs=sent_msgs, view=True)
    else:
        return render_template('mailbox.html', view=True)


@mailbox.route('/mailbox/received', methods = ['GET'])
def see_received_messages():
    if request.method == 'GET':
        rcv_msgs = db.session.query(Message).filter(Message.receiver==current_user.id) 
        return render_template('mailbox.html', rcv_msgs=rcv_msgs, view=False)
    else:
        return render_template('mailbox.html', view=False)
