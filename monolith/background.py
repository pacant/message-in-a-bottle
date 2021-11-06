from celery import Celery
import smtplib
from monolith.database import User, Message, db

BACKEND = BROKER = 'redis://localhost:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

_APP = None


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
            msg.delivered=True
            db.session.commit()
            print("delivered")

            usr = db.session.query(User).filter(
                User.id == msg.id_receiver
            ).first()

            try:
                mailserver = smtplib.SMTP('smtp.office365.com', 587)
                mailserver.ehlo()
                mailserver.starttls()
                mailserver.login('squad03MIB@outlook.com', 'StefanoForti')
                mailserver.sendmail('squad03MIB@outlook.com', usr.email, 'To:'+usr.email+
                    '\nFrom:squad03MIB@outlook.com\nSubject: New bottle received\n\nHey '+usr.firstname+
                    ',\nyou just received a new message in a bottle.\n\nGreetings,\nThe MIB team')
                mailserver.quit()
            except smtplib.SMTPRecipientsRefused:
                print("ERROR: SMTPRecipientsRefused ("+usr.email+")")


    else:
        app = _APP

    return []
