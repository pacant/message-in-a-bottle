from celery import Celery
from monolith.database import User, db

BACKEND = BROKER = 'redis://localhost:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(30.0, increase_trials, expires=10)


@celery.task
def increase_trials():
    from monolith.app import create_app
    app = create_app()
    db.init_app(app)

    with app.app_context():
        db.session.query(User).update({"trials": User.trials + 1})
        db.session.commit()
