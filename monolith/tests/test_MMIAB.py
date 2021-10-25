from datetime import date
import json
import unittest
import wtforms as f

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

    def test_auth(self):
        tested_app.config['WTF_CSRF_ENABLED'] = False
        app = tested_app.test_client()
        

        reply = app.get("/create_user")
        self.assertEqual(reply.status, '200 OK')

        reply = self.register(app, "prova_003@example.it", "Prova", "Example", "1234", "01/01/2001")
        self.assertEqual(reply.status, '200 OK')
        
        reply = self.login(app, "prova_003@example.it", "1234")

        self.assertIn(b"Hi",reply.data)
