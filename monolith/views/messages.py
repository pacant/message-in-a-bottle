from flask import Blueprint, request, jsonify, redirect
from dateutil import parser
from flask.templating import render_template
from monolith.background import send_message
import datetime
messages = Blueprint('messages', __name__)


@messages.route('/message/send', methods = ['GET','POST'])
def sendMessage():

    if request.method == 'POST':
        data = request.form
        print(data)
        date = parser.parse(request.form['date']+'+0200')
        result = send_message.apply_async((data,), eta = date)
        return render_template("send_message.html", message_ok = True)
    else:
        return render_template("send_message.html")

@messages.route('/show/message', methods = ['GET'])
def show_page():
    return render_template("send_message.html")