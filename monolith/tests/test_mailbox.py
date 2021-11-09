import unittest

from monolith.tests.test_base import TestBase
from monolith.database import db, User, Message


class TestApp(TestBase):

    def test_empty_inbox(self):

        user = 'user@example.com'

        self.register(user, "User", "User", "1234", "2001-01-01")
        self.login(user, "1234")

        reply = self.app.get("/mailbox/received")
        self.assertIn(b"No messages received !", reply.data)

        reply = self.app.post('/delete_user')
        self.assertEqual(reply.status, '302 FOUND')

    def test_empty_outbox(self):

        user = 'user@example.com'

        self.register(user, "User", "User", "1234", "2001-01-01")
        self.login(user, "1234")

        reply = self.app.get("/mailbox/sent")
        self.assertIn(b"No messages sent !", reply.data)

        reply = self.app.post('/delete_user')
        self.assertEqual(reply.status, '302 FOUND')

    def test_empty_draft(self):

        user = 'user@example.com'

        self.register(user, "User", "User", "1234", "2001-01-01")
        self.login(user, "1234")

        reply = self.app.get("/mailbox/draft")
        self.assertIn(b"No draft messages !", reply.data)

        reply = self.app.post('/delete_user')
        self.assertEqual(reply.status, '302 FOUND')

    def test_mailbox_sent(self):
        user = 'user@example.com'
        user_receiver = 'userrrrr@example.com'
        self.register(user, "User", "User", "1234", "2001-01-01")
        self.register(user_receiver, "User", "User", "1234", "2001-01-01")

        self.login(user, "1234")

        reply = self.app.get("/message/send")
        self.assertEqual(reply.status, '200 OK')

        message = dict(
            receiver=user_receiver,
            date='2020-11-03T01:01',
            text='Test message x')

        reply = self.app.post("/message/send",
                              data=message)
        self.assertEqual(reply.status, '200 OK')
        self.assertIn(b"Message sent correctly!", reply.data)

        reply = self.app.get("/mailbox/sent")
        self.assertIn(b'Test message x', reply.data)

        self.logout()
        self.login(user_receiver, "1234")

        reply = self.app.get("/mailbox/received", follow_redirects=True)
        self.assertIn(b'Test message x', reply.data)

        self.logout()

    def test_mailbox_draft(self):

        self.login(self.sender, "1234")

        reply = self.app.get("/message/send")
        self.assertEqual(reply.status, '200 OK')

        reply = self.app.get("/draft")
        self.assertEqual(reply.status, '405 METHOD NOT ALLOWED')

        message = dict(
            receiver=self.receiver,
            date='2020-10-26T01:01',
            text='DraftMessage')

        reply = self.app.post("/draft",
                              data=message)
        self.assertEqual(reply.status, '302 FOUND')

        #reply = app.get('/mailbox/draft')
        #self.assertIn(b'DraftMessage', reply.data)

        self.logout()
