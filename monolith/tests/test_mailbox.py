from datetime import date
import pytest
import unittest
import wtforms as f

from monolith.database import db, User, Message
from monolith.app import app as tested_app


class TestApp(unittest.TestCase):

    def register(self, client, email, firstname, lastname, password, dateofbirth):
        return client.post("/create_user",
                           data=dict(
                               email=email,
                               firstname=firstname,
                               lastname=lastname,
                               password=password,
                               dateofbirth=dateofbirth
                           ),
                           follow_redirects=True)
    
    def login(self, client, email, password):
        return client.post("/login",
                            data=dict(
                                email=email,
                                password=password
                            ),
                            follow_redirects=True)


    def test_outbox(self):
        user = 'prova_003@example.it'

        tested_app.config['WTF_CSRF_ENABLED'] = False
        app = tested_app.test_client()

        reply = self.register(app, user, "Prova", "Example", "1234", "01/01/2001")
        self.assertEqual(reply.status, '200 OK')
        
        reply = self.login(app, user, "1234")
        self.assertIn(b"Hi",reply.data)

        reply = app.get("/mailbox/sent")
        self.assertEqual(reply.status, '200 OK')

        reply = app.get("/delete_user")
        self.assertEqual(reply.status, '302 FOUND')
        

    def test_inbox(self):
        user = 'prova_003@example.it'

        tested_app.config['WTF_CSRF_ENABLED'] = False
        app = tested_app.test_client()

        reply = self.register(app, user, "Prova", "Example", "1234", "01/01/2001")
        self.assertEqual(reply.status, '200 OK')
        
        reply = self.login(app, user, "1234")
        self.assertIn(b"Hi",reply.data)

        reply = app.get("/mailbox/received")
        self.assertEqual(reply.status, '200 OK')

        reply = app.get("/delete_user")
        self.assertEqual(reply.status, '302 FOUND')


    def test_draft(self):
        user = 'prova_003@example.it'

        tested_app.config['WTF_CSRF_ENABLED'] = False
        app = tested_app.test_client()

        reply = self.register(app, user, "Prova", "Example", "1234", "01/01/2001")
        self.assertEqual(reply.status, '200 OK')
        
        reply = self.login(app, user, "1234")
        self.assertIn(b"Hi",reply.data)

        reply = app.get("/mailbox/draft")
        self.assertEqual(reply.status, '200 OK')

        reply = app.get("/delete_user")
        self.assertEqual(reply.status, '302 FOUND')