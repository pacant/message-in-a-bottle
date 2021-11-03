import unittest
from . import app, recipient, sender, register, login, logout
from monolith.database import db, User, Message


class TestApp(unittest.TestCase):

    def test_empty_inbox(self):

        user = 'user@example.com'

        register(app, user, "User", "User", "1234", "01/01/2001")
        login(app, user, "1234")

        reply = app.get("/mailbox/received")
        self.assertIn(b"No messages received !", reply.data)

        reply = app.get('/delete_user')
        self.assertEqual(reply.status, '302 FOUND')


    def test_empty_outbox(self):

        user = 'user@example.com'

        register(app, user, "User", "User", "1234", "01/01/2001")
        login(app, user, "1234")

        reply = app.get("/mailbox/sent")
        self.assertIn(b"No messages sent !", reply.data)

        reply = app.get('/delete_user')
        self.assertEqual(reply.status, '302 FOUND')


    def test_empty_draft(self):

        user = 'user@example.com'

        register(app, user, "User", "User", "1234", "01/01/2001")
        login(app, user, "1234")

        reply = app.get("/mailbox/draft")
        self.assertIn(b"No draft messages !", reply.data)

        reply = app.get('/delete_user')
        self.assertEqual(reply.status, '302 FOUND')


    def test_mailbox_sent(self):

        login(app, sender, "1234")

        reply = app.get("/message/send")
        self.assertEqual(reply.status, '200 OK')

        message = dict(
            receiver = recipient,
            date='2020-10-26T01:01',
            text='Test message')

        reply = app.post("/message/send",
                            data=message)
        self.assertEqual(reply.status, '200 OK')
        self.assertIn(b"Message sent correctly!",reply.data)

        reply = app.get("/mailbox/sent")
        self.assertIn(b'Test message', reply.data)

        logout(app)


    def test_mailbox_received(self):

        login(app, recipient, "1234")

        reply = app.get("/mailbox/received")
        self.assertIn(b'Test message', reply.data)

        logout(app)


    def test_mailbox_draft(self):

        login(app, sender, "1234")

        reply = app.get("/message/send")
        self.assertEqual(reply.status, '200 OK')

        reply = app.get("/draft")
        self.assertEqual(reply.status, '405 METHOD NOT ALLOWED')

        message = dict(
            receiver = recipient,
            date='2020-10-26T01:01',
            text='DraftMessage')

        reply = app.post("/draft",
                         data=message)
        self.assertEqual(reply.status, '302 FOUND')

        #reply = app.get('/mailbox/draft')
        #self.assertIn(b'DraftMessage', reply.data)
