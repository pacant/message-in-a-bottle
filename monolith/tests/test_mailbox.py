import unittest

from . import app, recipient, sender

class TestApp(unittest.TestCase):

    def test_mailbox_sent(self):
        reply = app.get("/mailbox/sent")
        self.assertIn(b"No messages sent !", reply.data)

    def test_mailbox_received(self):
        reply = app.get("mailbox/received")
        self.assertIn(b"No messages received !", reply.data)

    def test_mailbox_sent(self):
        reply = app.get("mailbox/draft")
        self.assertIn(b"No draft messages !", reply.data)
