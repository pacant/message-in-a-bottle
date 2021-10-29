from datetime import date
import pytest
import unittest
import wtforms as f

from monolith.database import db, User, Message
from monolith.app import app as tested_app


class TestApp(unittest.TestCase):

    def register(self, client, email, firstname, lastname, password, dateofbirdth):
        return client.post("/create_user",
                           data=dict(
                               email=email,
                               firstname=firstname,
                               lastname=lastname,
                               password=password,
                               dateofbirth=dateofbirdth
                           ),
                           follow_redirects=True)
    
    def login(self, client, email, password):
        return client.post("/login",
                            data=dict(
                                email=email,
                                password=password
                            ),
                            follow_redirects=True)


    def test_message_draft(self):
        sender = 'prova_003@example.it'
        recipient = 'prove_004@example.it'

        tested_app.config['WTF_CSRF_ENABLED'] = False
        app = tested_app.test_client()

        reply = self.register(app, sender, "Prova", "Example", "1234", "01/01/2001")
        self.assertEqual(reply.status, '200 OK')
        
        reply = self.login(app, sender, "1234")
        self.assertIn(b"Hi",reply.data)

        reply = app.get("/draft")
        self.assertEqual(reply.status, '405 METHOD NOT ALLOWED')

        message = dict(
            date='2020-10-26T01:01',
            text='Test message')

        reply = self.register(app, recipient, "Prova", "Example", "1234", "01/01/2001")
        self.assertEqual(reply.status, '200 OK')

        message['receiver']=recipient
        reply = app.post("/draft",
                            data=message)
        self.assertEqual(reply.status, '302 FOUND')

        reply = app.get("/delete_user")
        self.assertEqual(reply.status, '302 FOUND')

        reply = self.login(app, recipient, "1234")
        self.assertIn(b"Hi",reply.data)

        reply = app.get("/delete_user")
        self.assertEqual(reply.status, '302 FOUND')


    def test_message_send(self):
        sender = 'prova_003@example.it'
        recipient = 'prove_004@example.it'

        tested_app.config['WTF_CSRF_ENABLED'] = False
        app = tested_app.test_client()

        reply = app.get("/message/send")
        self.assertIn(b"Redirecting...",reply.data)

        reply = self.register(app, sender, "Prova", "Example", "1234", "01/01/2001")
        self.assertEqual(reply.status, '200 OK')
        
        reply = self.login(app, sender, "1234")
        self.assertIn(b"Hi",reply.data)

        reply = app.get("/message/send")
        self.assertEqual(reply.status, '200 OK')

        message = dict(
            date='2020-10-26T01:01',
            text='Test message')

        reply = self.register(app, recipient, "Prova", "Example", "1234", "01/01/2001")
        self.assertEqual(reply.status, '200 OK')

        message['receiver']=recipient
        reply = app.post("/message/send",
                            data=message)
        self.assertEqual(reply.status, '200 OK')
        self.assertIn(b"Message sent correctly!",reply.data)

        reply = app.get("/delete_user")
        self.assertEqual(reply.status, '302 FOUND')

        reply = self.login(app, recipient, "1234")
        self.assertIn(b"Hi",reply.data)

        reply = app.get("/delete_user")
        self.assertEqual(reply.status, '302 FOUND')
        # User.query.filter_by(email="prova_001@example.it").delete()


    def test_message_send_recipient_not_exists(self):
        sender = 'prova_003@example.it'
        recipient = 'prove_004@example.it'
        
        tested_app.config['WTF_CSRF_ENABLED'] = False
        app = tested_app.test_client()

        reply = self.register(app, sender, "Prova", "Example", "1234", "01/01/2001")
        self.assertEqual(reply.status, '200 OK')
        
        reply = self.login(app, sender, "1234")
        self.assertIn(b"Hi",reply.data)

        message = dict(
            date='2020-10-26T01:01',
            text='Test message')
        
        message['receiver']=recipient
        reply = app.post("/message/send",
                            data=message,
                            follow_redirects=True)
        self.assertEqual(reply.status, '400 Bad Request')

        reply = app.get("/delete_user")
        self.assertEqual(reply.status, '302 FOUND')


    def test_message_send_recipient_is_sender(self):
        sender = 'prova_003@example.it'
        
        tested_app.config['WTF_CSRF_ENABLED'] = False
        app = tested_app.test_client()

        reply = self.register(app, sender, "Prova", "Example", "1234", "01/01/2001")
        self.assertEqual(reply.status, '200 OK')
        
        reply = self.login(app, sender, "1234")
        self.assertIn(b"Hi",reply.data)

        message = dict(
            date='2020-10-26T01:01',
            text='Test message')
        
        message['receiver']=sender
        reply = app.post("/message/send",
                            data=message,
                            follow_redirects=True)
        self.assertEqual(reply.status, '400 Bad Request')

        reply = app.get("/delete_user")
        self.assertEqual(reply.status, '302 FOUND')


    def test_message_view(self):
        sender = 'prova_003@example.it'
        recipient = 'prove_004@example.it'
        id = 1

        tested_app.config['WTF_CSRF_ENABLED'] = False
        app = tested_app.test_client()

        reply = app.get("/message/"+str(id))
        self.assertIn(b"Redirecting...",reply.data)

        reply = self.register(app, sender, "Prova", "Example", "1234", "01/01/2001")
        self.assertEqual(reply.status, '200 OK')
        
        reply = self.login(app, sender, "1234")
        self.assertIn(b"Hi",reply.data)

        reply = app.get("/message/"+str(id))
        self.assertEqual(reply.status, '403 FORBIDDEN')

        reply = app.get("/message/"+str(id-2748923748927489))
        self.assertEqual(reply.status, '404 NOT FOUND')

        reply = app.get("/delete_user")
        self.assertEqual(reply.status, '302 FOUND')
