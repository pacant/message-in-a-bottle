from flask import Blueprint, request, jsonify
from dateutil import parser
from monolith.background import send_message
messages = Blueprint('messages', __name__)


@messages.route('/message/send', methods = ['POST'])
def sendMessage():
    data = request.get_json()
    date = parser.parse(data['date'])
    result = send_message.apply_async((data,), eta = date)
    return jsonify({"msg":"Message sent!"})

