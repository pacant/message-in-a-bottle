import datetime
import pytest
import unittest
import wtforms as f

from monolith.database import db, User, Message
from monolith.tests.test_base import TestBase


class TestApp(TestBase):

    def test_message_draft(self):

        self.login(self.sender, "1234")

        reply = self.app.get("/draft")
        self.assertEqual(reply.status, '405 METHOD NOT ALLOWED')

        message = dict(
            receiver=self.receiver,
            date='2020-10-26T01:01',
            text='Draft message')

        reply = self.app.post("/draft", data=message)
        self.assertEqual(reply.status, '302 FOUND')

        self.logout()

    def test_message_send(self):

        #reply = app.get("/message/send")
        # self.assertIn(b"Redirecting...",reply.data)

        self.login(self.sender, "1234")

        reply = self.app.get("/message/send")
        self.assertEqual(reply.status, '200 OK')

        message = dict(
            receiver=self.receiver,
            date='2020-10-26t01:01',
            text='test message')

        reply = self.app.post("/message/send",
                              data=message)
        self.assertEqual(reply.status, '200 OK')
        self.assertIn(b"Message sent correctly!", reply.data)

        self.logout()

    def test_message_send_recipient_not_exists(self):

        self.login(self.sender, "1234")

        message = dict(
            receiver="mailnotexists@gmail.com",
            date='2020-10-26T01:01',
            text='Test message')

        reply = self.app.post("/message/send",
                              data=message,
                              follow_redirects=True)
        self.assertIn(b"Unable to send bottle to 'mailnotexists@gmail.com'", reply.data)
        self.logout()

    def test_message_send_recipient_is_sender(self):

        self.login(self.sender, "1234")

        message = dict(
            receiver=self.sender,
            date='2020-10-26T01:01',
            text='Test message')

        reply = self.app.post("/message/send",
                              data=message,
                              follow_redirects=True)
        self.assertIn(b"Unable to send bottle to '" + self.sender.encode('utf8') + b"'", reply.data)

        self.logout()

    def test_message_view(self):
        self.login(self.sender, "1234")

        msg_date = (datetime.datetime.now() - datetime.timedelta(days=10)).isoformat()
        message = dict(
            receiver=self.receiver,
            date=msg_date,
            text='test_message_view_' + msg_date)

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
        self.assertEqual(reply.status, '200 OK')

        self.logout()

    def test_message_view_not_delivered(self):
        self.login(self.sender, "1234")

        msg_date = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
        message = dict(
            receiver=self.receiver,
            date=msg_date,
            text='test_message_view_not_delivered_' + msg_date)

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

        self.logout()

    def test_message_view_unauthorized(self):
        self.login(self.sender, "1234")

        msg_date = (datetime.datetime.now() - datetime.timedelta(days=10)).isoformat()
        message = dict(
            receiver=self.receiver,
            date=msg_date,
            text='test_message_view_unauthorized_' + msg_date)

        reply = self.app.post("/message/send",
                              data=message,
                              follow_redirects=True)
        self.assertEqual(reply.status, '200 OK')

        id = 0
        from monolith.app import app
        with app.app_context():
            id = db.session.query(Message).filter(Message.text == message['text']).first().id

        self.logout()

        reply = self.app.get("/message/" + str(id))
        self.assertEqual(reply.status, '401 UNAUTHORIZED')

        self.login(self.other, '1234')

        reply = self.app.get("/message/" + str(id))
        self.assertEqual(reply.status, '403 FORBIDDEN')

        self.logout()

    def test_message_view_not_found(self):
        self.login(self.sender, '1234')

        reply = self.app.get("/message/" + str(2748923748927489))
        self.assertEqual(reply.status, '404 NOT FOUND')

        self.logout()

    def test_recipients(self):

        self.login(self.sender, "1234")

        reply = self.app.get('/message/recipients')
        self.assertEqual(reply.status, '200 OK')
        self.assertIn(b'Search recipient', reply.data)

        self.logout()

    def test_send_image(self):

        self.login(self.sender, "1234")
        with open("monolith/index.png", "rb") as image:
            f = image.read()
            data = dict(file=f)
            message = dict(
                receiver=self.receiver,
                date='2020-10-26t01:01',
                text='test_send_image',
                file=image)

            reply = self.app.post("/message/send", content_type='multipart/form-data',
                                  data=message, follow_redirects=True)
            reply = self.app.get('/mailbox/sent')
            self.assertIn(b"test_send_image", reply.data)

            self.logout()

            id = 0
            from monolith.app import app
            with app.app_context():
                id = db.session.query(Message).filter(Message.text == 'test_send_image').first().id

            self.login(self.receiver, '1234')

            reply = self.app.get("/message/" + str(id))
            self.assertEqual(reply.status, '200 OK')

            self.logout()

    def test_forward(self):
        self.login(self.sender, '1234')

        message = dict(
            receiver=self.receiver,
            date='2020-10-26t01:01',
            text='message forward',
        )

        reply = self.app.post("/message/send", data=message, follow_redirects=True)

        self.logout()

        self.login(self.receiver, '1234')

        reply = self.app.get('/mailbox/received')
        self.assertIn(b'message forward', reply.data)

        id = 0
        from monolith.app import app
        with app.app_context():
            id = db.session.query(Message).filter(Message.text == message['text']).first().id

        reply = self.app.get('message/recipients/' + str(id))
        self.assertIn(b'Search recipient', reply.data)

        message = dict(
            recipient=self.receiver
        )

        reply = self.app.get('message/forward/' + str(id), data=message)
        self.assertIn(b'message forward', reply.data)

        self.logout()

    def test_group_message(self):
        self.login(self.sender, '1234')

        message = dict(
            receiver=self.receiver + ', ' + self.other,
            date='2020-10-26t01:01',
            text='group message',
        )

        reply = self.app.post("/message/send", data=message)
        self.assertEqual(reply.status, '200 OK')
        self.logout()

        self.login(self.receiver, '1234')

        reply = self.app.get('/mailbox/received')
        self.assertIn(b'group message', reply.data)

        self.logout()

        self.login(self.other, '1234')

        reply = self.app.get('/mailbox/received')
        self.assertIn(b'group message', reply.data)

        self.logout()

    def test_zwithdraw_message(self):

        from monolith.app import app

        user = "igp@gmail.com"
        self.register(user, "User", "User", "1234", "2001-01-01")
        self.login(user, "1234")
        with app.app_context():
            db.session.query(User).filter(User.email == user).update({"points": 20})
            db.session.commit()

        date = datetime.datetime.now() + datetime.timedelta(minutes=360)
        with app.app_context():
            db.session.query(User).filter(User.email == user).update({"points": 20})
            print(db.session.query(User).filter(User.email == user).first().points)
            db.session.commit()

        message = dict(
            receiver=self.receiver,
            date=date,
            text='message withdraw')

        reply = self.app.post("/message/send",
                              data=message)

        reply = self.app.get("/mailbox/sent")
        self.assertIn(b'message withdraw', reply.data)

        id = 0
        with app.app_context():
            id = db.session.query(Message).filter(Message.text == message['text']).first().id

        reply = self.app.post("/message/withdraw/" + str(id), follow_redirects=True)

        self.assertIn(b"No messages sent !", reply.data)
        self.logout()

    def test_zzdelete_message(self):

        from monolith.app import app

        user = "igp@gmail.com"
        with app.app_context():
            id = db.session.query(User).filter(User.email == user).first()

        self.register(user, "User", "User", "1234", "2001-01-01")
        self.login(user, "1234")
        date = datetime.datetime.now()

        message = dict(
            receiver=self.receiver,
            date='2020-10-26t01:01',
            text='message delete')

        reply = self.app.post("/message/send",
                              data=message)

        self.logout()
        self.login(self.receiver, "1234")
        id = 0

        reply = self.app.get("/mailbox/received")
        self.assertIn(b"message delete", reply.data)

        with app.app_context():
            id = db.session.query(Message).filter(Message.text == message['text']).first().id

        reply = self.app.post("/message/" + str(id) + "/delete", follow_redirects=True)

        self.assertNotIn(b"message delete", reply.data)
        with app.app_context():
            db.session.query(Message).filter(Message.id == id).delete()
            db.session.commit()

        self.logout()
