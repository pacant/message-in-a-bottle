from celery import Celery

from monolith.database import Message, db

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
            db.session.query(Message).filter(
                Message.id == id_message).update({"delivered": True})

            db.session.commit()
            print("delivered")

    else:
        app = _APP

    return []
