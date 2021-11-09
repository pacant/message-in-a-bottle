from datetime import datetime
from flask import Blueprint, request, redirect, abort
from flask_login.utils import login_required
from monolith.database import ContentFilter, UserContentFilter, Attachments, Message, User, Blacklist, db
from dateutil import parser
from flask.templating import render_template
from flask_login import current_user
from monolith.background import send_message as send_message_task
import base64
import re
import json
import smtplib

messages = Blueprint('messages', __name__)


@messages.route('/message/send/<id_message>', methods=['GET', 'POST'])
@login_required
def send_draft(id_message):
    if request.method == 'POST':

        send_message_async(request.form)
        db.session.query(Message).filter(Message.id == id_message).delete()
        db.session.commit()
        return render_template("send_message.html", form=dict(), message_ok=True)
    else:
        message = db.session.query(Message).filter(Message.id == id_message).first()
        receiver = db.session.query(User).filter(User.id == message.id_receiver).first().email
        date = message.date_delivery.isoformat()
        text = message.text
        form = dict(recipient=receiver, text=text, date=date, message_id=message.id)
        return render_template("send_message.html", form=form)


@ messages.route('/message/send', methods=['GET', 'POST'])
@login_required
def send_message():
    if request.method == 'POST':

        emails = request.form.get('receiver').split(',')

        for email in emails:
            if db.session.query(User).filter(User.email == email,
                                             User.is_active.is_(True), User.email != current_user.email).first() is None:
                abort(400)

        for email in emails:
            new_form = dict(
                receiver=email,
                date=request.form.get('date'),
                text=request.form.get('text')
            )
            send_message_async(new_form)

        return render_template("send_message.html", form=dict(), message_ok=True)
    else:
        # landing from the recipients page, we want to populate the field with the chosen one
        recipient_message = request.args.items(multi=True)
        rec_list = []

        for item in recipient_message:
            item = item[1].strip('\'')
            rec_list.append(item)

        rec_list[:] = [x for x in rec_list if x]
        rec_list = list(dict.fromkeys(rec_list))

        recipients = ''

        for i in range(len(rec_list)):
            if i == (len(rec_list) - 1):
                recipients = recipients + rec_list[i]
            else:
                recipients = recipients + rec_list[i] + ', '

        form = dict(recipient=recipients)

        return render_template("send_message.html", form=form)


@ messages.route('/draft', methods=['POST'])
@ login_required
def draft():
    data = request.form
    save_message(data)
    return redirect('/mailbox/draft')


@ messages.route('/message/forward/<id_message>', methods=['POST'])
@ login_required
def send_forward_msg(id_message):
    recipient_message = request.form['recipient']
    text = db.session.query(Message).filter(Message.id == id_message).first().text
    form = dict(recipient=recipient_message, text=text, message_id=id_message)
    return render_template("send_message.html", form=form, forward=True)


@ messages.route("/message/recipients", methods=["GET"])
@ login_required
def chooseRecipient():
    email = current_user.email
    recipients = db.session.query(User).filter(User.email != email).filter(
        User.is_admin.is_(False)).filter(
            User.is_reported.is_(False)).filter(
                User.is_active.is_(True)
    )
    form = dict(recipients=recipients)
    return render_template("recipients.html", form=form)


@ messages.route('/message/recipients/<id_message>', methods=['GET'])
@ login_required
def choose_recipient_msg(id_message):
    email = current_user.email
    recipients = db.session.query(User).filter(User.email != email)
    form = dict(recipients=recipients, id_message=id_message)
    return render_template("recipients.html", form=form)


@ messages.route('/message/<message_id>')
@ login_required
def viewMessage(message_id):
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

        if int(message.Message.id_receiver) == current_user.id and not message.Message.read:
            notify_msg_reading(message)

        # if message contains bad words they are not showed
        if int(message.Message.id_sender) != current_user.id:
            message.Message.text = purify_message(message.Message.text)

        images_db = db.session.query(Attachments).filter(Attachments.id_message == message_id).all()
        images = []
        for image in images_db:
            images.append(base64.b64encode(image.data).decode('ascii'))
        print(images)
        return render_template("message.html",
                               sender=message.User,
                               recipient=recipient,
                               message=message.Message,
                               images=images,
                               date='-')


def send_message_async(data):
    email = data['receiver'].strip('\', [, ]')
    recipient = db.session.query(User).filter(User.email == email).all()
    result = db.session.query(Blacklist).filter(
        Blacklist.id_user == recipient[0].id).filter(
            Blacklist.id_blacklisted == current_user.id).all()
    date = parser.parse(data['date'] + '+0100')
    id_message = save_message(data)

    if not result:
        send_message_task.apply_async((id_message,), eta=date)
    else:
        return


def save_message(data):

    message = Message()
    message.text = data['text']
    id_receiver = db.session.query(User).filter(
        User.email == data['receiver'].strip('\', [, ]')).first().id
    message.id_receiver = id_receiver
    message.id_sender = current_user.id
    message.draft = True if 'draft' in data else False
    message.date_delivery = parser.parse(data['date'] + '+0100')
    message.date_send = datetime.now()
    message.deleted = False

    db.session.add(message)
    db.session.commit()

    for file in request.files:
        attachment = Attachments()
        attachment.id_message = message.id
        attachment.data = request.files[file].read()
        db.session.add(attachment)

    db.session.commit()

    return message.id


def purify_message(msg):
    list = db.session.query(UserContentFilter.id_content_filter).filter(
        UserContentFilter.id_user == current_user.id
    )

    personal_filters = db.session.query(ContentFilter, UserContentFilter).filter(
        ContentFilter.id.in_(list)
    ).join(UserContentFilter, isouter=True).union_all(
        db.session.query(ContentFilter, UserContentFilter).filter(
            ContentFilter.private.is_(False), UserContentFilter.active.is_(True)
        ).join(UserContentFilter, isouter=True)
    ).all()

    purified_message = msg

    for personal_filter in personal_filters:
        for word in json.loads(personal_filter.ContentFilter.words):
            insensitive_word = re.compile(re.escape(word), re.IGNORECASE)
            purified_message = insensitive_word.sub('*' * len(word), purified_message)
    return purified_message


def notify_msg_reading(message):
    message.Message.read = True
    db.session.commit()
    try:
        mailserver = smtplib.SMTP('smtp.office365.com', 587)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.login('squad03MIB@outlook.com', 'StefanoForti')
        mailserver.sendmail('squad03MIB@outlook.com', message.User.email, 'To:' + message.User.email +
                            '\nFrom:squad03MIB@outlook.com\nSubject:Message reading notification\n\n' +
                            current_user.firstname +
                            ' have just read your message in a bottle.\n\nGreetings,\nThe MIB team')
        mailserver.quit()
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPDataError, smtplib.SMTPConnectError,
            smtplib.SMTPNotSupportedError, smtplib.SMTPSenderRefused, smtplib.SMTPServerDisconnected,
            smtplib.SMTPHeloError) as e:
        print("ERROR: " + str(e))


@ messages.route("/message/withdraw/<id>", methods=['POST'])
@ login_required
def withdraw_message(id):
    message_query = db.session.query(Message, User).filter(
        Message.id == int(id)
    ).join(User, Message.id_sender == User.id)
    message = message_query.first()

    if message is None or (int(message.Message.id_receiver) == current_user.id):
        abort(404)
    elif int(message.Message.id_sender) != current_user.id and int(message.Message.id_receiver) != current_user.id:
        abort(403)
    elif (message.Message.delivered is True) or (message.User.points < 10):
        return redirect("/mailbox/sent")
    else:
        db.session.query(User).filter(User.id == current_user.id).update({"points": User.points - 10})
        db.session.query(Message).filter(Message.id == int(id)).delete()
        db.session.commit()
        return redirect('/mailbox/sent')


@ messages.route('/message/<message_id>/delete', methods=["POST"])
@login_required
def deleteMessage(message_id):
    message = db.session.query(Message, User).filter(
        Message.id == int(message_id)
    ).join(User, Message.id_sender == User.id).first()

    if message is None or (int(message.Message.id_receiver) == current_user.id and not message.Message.delivered):
        abort(404)
    elif int(message.Message.id_sender) != current_user.id and int(message.Message.id_receiver) != current_user.id:
        abort(403)
    else:
        db.session.query(Message).filter(Message.id == int(message_id)).update({"deleted": True})
        db.session.commit()
        return redirect('/mailbox/received')


@ messages.route("/calendar/sent")
@ login_required
def calendar_sent():
    msgs_sent = db.session.query(Message, User).filter(
        Message.id_receiver == User.id).filter(
            Message.id_sender == current_user.id).filter(Message.delivered).all()

    return render_template("calendar.html", msgs_sent=msgs_sent)


@ messages.route("/calendar/received")
@ login_required
def calendar_received():
    msgs_rcv = db.session.query(Message, User).filter(
        Message.id_sender == User.id).filter(
            Message.id_receiver == current_user.id).filter(Message.delivered).filter(Message.deleted.is_(False)).all()

    return render_template("calendar.html", msgs_rcv=msgs_rcv)
