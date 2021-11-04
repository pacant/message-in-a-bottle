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

    def test_add_to_blacklist(self):
        self.login(self.sender,"1234")
        reply = self.app.post('/blacklist/add', data=self.receiver, follow_redirects=True)
        self.assertEqual(reply.status, '200 OK')
        #self.assertIn(b'prove_004@example.it', reply.data)
        self.logout()
