from celery import Celery

from monolith.database import User, Message, db

BACKEND = BROKER = 'redis://localhost:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

_APP = None


@celery.task
def send_message(data):
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
        message = Message()
        
        with app.app_context():
            message.text = data['text']
            message.sender= data['sender']
            message.receiver= data['receiver']
            db.session.add(message)
            db.session.commit()
            print(message)

    else:
        app = _APP

    return []

