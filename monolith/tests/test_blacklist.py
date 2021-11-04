import unittest

from flask import app

from monolith.tests.test_base import TestBase
from monolith.database import db, User, Message, Blacklist


class TestApp(TestBase):

    def test_empty_blacklist(self):

        reply = self.login(self.sender, "1234")

        reply = self.app.get('/blacklist')
        self.assertIn(b'No users in blacklist !', reply.data)
        self.logout()

    def test_fadd_to_blacklist(self):
        self.login(self.sender, "1234")
        reply = self.app.post('/blacklist/add', data=dict(email=self.receiver), follow_redirects=True)
        self.assertEqual(reply.status, '200 OK')
        self.assertIn(b'prova1@gmail.com', reply.data)

        reply=self.app.post('/blacklist/remove', data=dict(email=self.receiver), follow_redirects=True)
        self.assertIn(b'No users in blacklist !', reply.data)
        self.logout()
