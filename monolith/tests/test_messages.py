from datetime import date
import pytest
import unittest
import wtforms as f

from monolith.database import db, User, Message
from . import app, recipient, sender
class TestApp(unittest.TestCase):


    def test_message_draft(self):

        reply = app.get("/draft")
        self.assertEqual(reply.status, '405 METHOD NOT ALLOWED')

        message = dict(
            receiver = recipient,
            date='2020-10-26T01:01',
            text='Test message')

        reply = app.post("/draft",
                            data=message)
        self.assertEqual(reply.status, '302 FOUND')


    def test_message_send(self):

        #reply = app.get("/message/send")
        #self.assertIn(b"Redirecting...",reply.data)



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

        # User.query.filter_by(email="prova_001@example.it").delete()


    def test_message_send_recipient_not_exists(self):


        message = dict(
            receiver = recipient,
            date='2020-10-26T01:01',
            text='Test message')

        reply = app.post("/message/send",
                            data=message,
                            follow_redirects=True)
        #self.assertEqual(reply.status, '400 Bad Request')



    def test_message_send_recipient_is_sender(self):
        message = dict(
            receiver = recipient,
            date='2020-10-26T01:01',
            text='Test message')

        reply = app.post("/message/send",
                            data=message,
                            follow_redirects=True)
        self.assertEqual(reply.status, '200 OK')

    def test_message_view(self):
        id = 1

        reply = app.get("/message/"+str(id))
        self.assertEqual(reply.status, '403 FORBIDDEN')

        reply = app.get("/message/"+str(id-2748923748927489))
        self.assertEqual(reply.status, '404 NOT FOUND')

        reply = app.get("/delete_user")
        self.assertEqual(reply.status, '302 FOUND')

    def test_recipients(self):

        app.get('/message/recipients')

