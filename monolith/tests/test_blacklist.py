import datetime

from flask import app

from monolith.tests.test_base import TestBase
from monolith.database import db, User, Message, Blacklist


class TestApp(TestBase):

    def test_empty_blacklist(self):

        reply = self.login(self.sender, "1234")

        reply = self.app.get('/blacklist')
        self.assertIn(b'No users in blacklist !', reply.data)
        self.logout()

    def test_user_add_to_blacklist(self):
        self.login(self.sender, "1234")

        reply = self.app.get('/blacklist/add')
        self.assertIn(b'Choose a user', reply.data)

        reply = self.app.post('/blacklist/add', data=dict(email=self.receiver), follow_redirects=True)
        self.assertEqual(reply.status, '200 OK')
        self.assertIn(b'prova1@gmail.com', reply.data)

        reply = self.app.get('/blacklist')
        self.assertIn(b'prova1@gmail.com', reply.data)

        reply=self.app.post('/blacklist/remove', data=dict(email=self.receiver), follow_redirects=True)
        self.assertIn(b'No users in blacklist !', reply.data)
        self.logout()

    def test_user_add_to_blacklist_send_message(self):
        self.login(self.receiver, "1234")

        reply = self.app.get('/blacklist/add')
        self.assertIn(b'Choose a user', reply.data)

        reply = self.app.post('/blacklist/add', data=dict(email=self.sender), follow_redirects=True)
        self.assertEqual(reply.status, '200 OK')
        self.assertIn(self.sender.encode('utf-8'), reply.data)

        reply = self.app.get('/blacklist')
        self.assertIn(self.sender.encode('utf-8'), reply.data)

        self.logout()

        self.login(self.sender, '1234')

        msg_date = (datetime.datetime.now() - datetime.timedelta(days=10)).isoformat()
        message = dict(
            receiver=self.receiver,
            date=msg_date,
            text='test_user_add_to_blacklist_send_message_' + msg_date)

        reply = self.app.post("/message/send",
                              data=message,
                              follow_redirects=True)
        self.assertEqual(reply.status, '200 OK')

        
        id = 0
        from monolith.app import app
        with app.app_context():
            id = db.session.query(Message).filter(Message.text == message['text']).first().id

        reply = self.app.get("/message/" + str(id))
        self.assertEqual(reply.status, '200 OK')

        self.logout()

        self.login(self.receiver, '1234')

        reply = self.app.get("/message/" + str(id))
        self.assertEqual(reply.status, '404 NOT FOUND')

        reply=self.app.post('/blacklist/remove', data=dict(email=self.sender), follow_redirects=True)
        self.assertIn(b'No users in blacklist !', reply.data)

        self.logout()
