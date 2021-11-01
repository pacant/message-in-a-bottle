from celery import Celery
from monolith.database import db, Message
app = Celery('tasks', broker='redis://localhost')

@app.task
def send_message(data):
    message = Message()
    message.text = data['text']
    message.sender= data['sender']
    message.receiver= data['receiver']
    db.session.add(message)
    db.session.commit()
    print(message)