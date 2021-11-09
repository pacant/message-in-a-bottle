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
        reply = self.app.get("/calendar/sent" , follow_redirects=True)
        reply = self.app.get("/calendar/received" , follow_redirects=True)
        self.logout()
