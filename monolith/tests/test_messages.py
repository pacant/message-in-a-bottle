
from datetime import date
import json
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

    def test_send_message(self):
        tested_app.config['WTF_CSRF_ENABLED'] = False
        app = tested_app.test_client()

        db.init_app(tested_app)
        tested_app.app_context().push()

        self.register(app, "prova_001@example.it", "Giulio", "Example", "1234", "01/01/2001")
        self.register(app, "prova_002@example.it", "Antonio", "Example", "1234", "01/01/2001")

        self.login(app, "prova_002@example.it", "1234")

        reply = app.post("/message/send",
                    data=dict(
                        text="Ciao Giulio",
                        receiver="prova_001@example.it",
                        date = "2021-10-28T00:10"
                    ))

        self.assertIn(b"Message sent correctly!", reply.data)
        User.query.filter_by(email="prova_001@example.it").delete()
