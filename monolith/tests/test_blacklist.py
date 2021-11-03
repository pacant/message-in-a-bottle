import unittest
from . import app, recipient, sender, register, login, logout
from monolith.database import db, User, Message, Blacklist


class TestApp(unittest.TestCase):

    def test_empty_blacklist(self):

        user = 'user@example.com'

        register(app, user, "User", "User", "1234", "01/01/2001")
        login(app, user, "1234")

        reply = app.get('/blacklist')
        self.assertIn(b'No users in blacklist !', reply.data)

        reply = app.get('/delete_user')
        self.assertEqual(reply.status, '302 FOUND')


    def test_add_to_blacklist(self):

        login(app, sender, "1234")

        reply = app.post('/blacklist/add', data=recipient)
        self.assertEqual(reply.status, '302 FOUND')
        self.assertIn(b'prove_004@example.it', reply.data)
