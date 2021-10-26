from flask import Blueprint, request, jsonify, redirect
from dateutil import parser
from flask.globals import current_app
from flask.templating import render_template
from flask_login import current_user
from monolith.background import send_message
from monolith.database import User, db
messages = Blueprint('messages', __name__)


@messages.route('/message/send', methods = ['GET','POST'])
def sendMessage():
    if current_user is not None and hasattr(current_user, 'id'):
        if request.method == 'POST':
            data = request.form
            print(data)
            date = parser.parse(request.form['date']+'+0200')
            message = {
                "text":data['text'],
                "id_sender":current_user.id,
                "receiver":request.form.get("recipient")
            }
            result = send_message.apply_async((message,), eta = date)
            return render_template("send_message.html", message_ok = True)
        else:
            return render_template("send_message.html")
    else:
        return redirect('/')

@messages.route("/message/recipients", methods =["GET","POST"])
def chooseRecipient():
    if request.method == "GET":
        print("ciao")
        email = current_user.email
        print(email)
        recipients = db.session.query(User).filter(User.email != email)
        return render_template("recipients.html", recipients=recipients)
    if request.method == "POST":
        recipient = request.form.get("recipient")
        return render_template("send_message.html", recipient=recipient)
