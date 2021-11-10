from datetime import date
import unittest

from monolith.tests.test_base import TestBase
import wtforms as f

from monolith.app import app as tested_app
from monolith.database import db, User, Message
from monolith.views.messages import draft


class TestApp(TestBase):

    def test_draft(self):

        reply = self.login(self.sender, "1234")
        self.assertIn(b"Hi", reply.data)

        message = dict(
            receiver=self.receiver,
            date='2020-10-26T01:01',
            text='test_draft_2020-10-26T01:01',
            draft = True)

        reply = self.app.post("/draft",
                         data=message, follow_redirects = True)
        self.assertIn(message['text'].encode('utf-8'), reply.data)

        id = 0
        from monolith.app import app
        with app.app_context():
            id = db.session.query(Message).filter(Message.text == message['text']).first().id

        reply = self.app.get("/message/send/" + str(id), follow_redirects=True)
        self.assertIn(message['text'].encode('utf-8'), reply.data)
        reply = self.app.post("/message/send/" + str(id), data=message)
        self.logout()
