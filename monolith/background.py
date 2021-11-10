from celery import Celery
import smtplib
from monolith.database import User, Message, db

BACKEND = BROKER = 'redis://localhost:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

_APP = None


def internal_send_email(to, subject, message):
    try:
        mailserver = smtplib.SMTP('smtp.office365.com', 587)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.login('squad03MIB@outlook.com', 'AntonioBrogi')
        mailserver.sendmail('squad03MIB@outlook.com', to, 'To:' + to +
                            '\nFrom:squad03MIB@outlook.com\nSubject: ' + subject + '\n\n' +
                            message)
        mailserver.quit()
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPDataError, smtplib.SMTPConnectError,
            smtplib.SMTPNotSupportedError, smtplib.SMTPSenderRefused, smtplib.SMTPServerDisconnected,
            smtplib.SMTPHeloError, smtplib.SMTPAuthenticationError) as e:
        print("ERROR: " + str(e))


@celery.task
def send_message(id_message):
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)

        with app.app_context():
            msg = db.session.query(Message).filter(
                Message.id == id_message).first()
            msg.delivered = True
            db.session.commit()
            print("delivered")

            usr = db.session.query(User).filter(
                User.id == msg.id_receiver
            ).first()

            internal_send_email(usr.email, 'New bottle received',
                                'Hey ' + usr.firstname +
                                ',\nyou just received a new message in a bottle.\n\nGreetings,\nThe MIB team')

    else:
        app = _APP

    return []


@celery.task
def send_notification(message_id, current_user_firstname):
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)

        with app.app_context():
            message = db.session.query(Message, User).filter(
                Message.id == int(message_id)
            ).join(User, Message.id_sender == User.id).first()
            message.Message.read = True
            db.session.commit()
            internal_send_email(message.User.email, 'Message reading notification',
                                current_user_firstname +
                                ' have just read your message in a bottle.\n\nGreetings,\nThe MIB team')
    else:
        app = _APP

    return []
