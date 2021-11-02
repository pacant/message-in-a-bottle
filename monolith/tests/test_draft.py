from datetime import date
import unittest
import wtforms as f

from monolith.app import app as tested_app
from monolith.database import db, User, Message
from monolith.views.messages import draft


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

    def unregister(self, client):
        return client.post("/delete_user")

    def test_draft(self):
        sender = 'prova_003@example.it'
        recipient = 'prove_004@example.it'

        tested_app.config['WTF_CSRF_ENABLED'] = False
        app = tested_app.test_client()

        reply = self.register(app, sender, "Prova", "Example", "1234", "01/01/2001")
        self.assertEqual(reply.status, '200 OK')
        reply = self.register(app, recipient, "Prova", "Example", "1234", "01/01/2001")

        reply = self.login(app, sender, "1234")
        self.assertIn(b"Hi", reply.data)

        message = dict(
            receiver=recipient,
            date='2020-10-26T01:01',
            text='Testmessage1')

        reply = app.post("/draft",
                         data=message)

        message_id = db.session.query(Message).filter(
            Message.text == "Testmessage1" and Message.draft.is_(True)).first().id
        reply = app.get("/message/send/" + str(message_id))
        self.assertIn(b"Testmessage1", reply.data)
        reply = app.post("/message/send/" + str(message_id), data=message)
