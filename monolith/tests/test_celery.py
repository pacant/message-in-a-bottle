from datetime import date
import datetime
import unittest

from monolith.tests.test_base import TestBase
import wtforms as f

from monolith.app import app as tested_app
from monolith.database import db, User, Message
from monolith.views.messages import draft
from monolith.lottery import increase_trials
from monolith.background import send_message

class TestApp(TestBase):
    def test_increase(self):
        self.login(self.sender, "1234")
        self.app.get("/lottery")
        increase_trials.apply()
        reply = self.app.post("/spin")
        self.assertIn(b"YOU WON",reply.data)
        reply = self.app.post("/spin")
        self.assertNotIn(b"YOU WON",reply.data)
        self.logout()

    def test_send_message_celery(self):
        from monolith.app import app

        user = "igp12345@gmail.com"
        user_receiver = "igp234@gmail.com"
        self.register(user, "User", "User", "1234", "2001-01-01")
        self.register(user_receiver, "User", "User", "1234", "2001-01-01")
        self.login(user, "1234")


        date = datetime.datetime.now() + datetime.timedelta(minutes=360)

        message = dict(
            receiver=user_receiver,
            date=date,
            text='message celery')

        reply = self.app.post("/message/send",
                              data=message)

        id = 0
        with app.app_context():
            id = db.session.query(Message).filter(Message.text == message['text']).first().id

        send_message.apply((id,))

        self.logout()
