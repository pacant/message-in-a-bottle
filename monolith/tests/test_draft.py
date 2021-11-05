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
            text='Testmessage1',
            draft = True)

        reply = self.app.post("/draft",
                         data=message, follow_redirects = True)
        self.assertIn(b"Testmessage", reply.data)

        reply = self.app.get("/message/send/" + str(1), follow_redirects=True)
        self.assertIn(b"Testmessage1", reply.data)
        reply = self.app.post("/message/send/" + str(1), data=message)
        self.logout()
