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


    def test_create_user(self):
        user = 'prova_003@example.it'

        tested_app.config['WTF_CSRF_ENABLED'] = False
        app = tested_app.test_client()

        reply = self.register(app, user, "Prova", "Example", "1234", "01/01/2001")
        self.assertEqual(reply.status, '200 OK')

        reply = app.put("/create_user",
                           data=dict(
                               email='prova_003@example.it',
                               firstname='prova',
                               lastname='example',
                               password='prova',
                               dateofbirth='01/01/1970'
                           ),
                           follow_redirects=True)
        self.assertEqual(reply.status, '405 METHOD NOT ALLOWED')

        reply = self.login(app, user, "1234")
        self.assertIn(b"Hi",reply.data)

        reply = app.get("/delete_user")
        self.assertEqual(reply.status, '302 FOUND')
        

    def test_userinfo(self):
        user = 'prova_003@example.it'

        tested_app.config['WTF_CSRF_ENABLED'] = False
        app = tested_app.test_client()

        reply = self.register(app, user, "Prova", "Example", "1234", "01/01/2001")
        self.assertEqual(reply.status, '200 OK')
        
        reply = self.login(app, user, "1234")
        self.assertIn(b"Hi",reply.data)

        reply = app.get("/userinfo")
        self.assertEqual(reply.status, '200 OK')

        reply = app.get("/delete_user")
        self.assertEqual(reply.status, '302 FOUND')