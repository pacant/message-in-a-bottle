import datetime
from time import sleep

from monolith.database import db, User, Message
from monolith.tests.test_base import TestBase


class TestApp(TestBase):
    def test_login(self):
        reply = self.app.post("/login",
                              data=dict(
                                  email="email",
                                  pasword="password"
                              ),
                              follow_redirects=True)
        self.assertEqual(reply.status, '400 BAD REQUEST')

    def test_user_list(self):
        self.login(self.sender, "1234")
        reply = self.app.get("/users")
        self.assertIn(b'User List', reply.data)
        self.logout()

    def test_recipients(self):
        self.login(self.sender, "1234")
        reply = self.app.get("/message/recipients")
        self.assertIn(b'prova1@gmail.com', reply.data)
        self.logout()

    def test_create_user_page(self):
        self.login(self.sender, "1234")
        reply = self.app.get("/create_user")
        self.assertIn(b'email', reply.data)

        reply = self.app.post("/create_user",
                              data=dict(
                                  email=self.sender,
                                  firstname='Prova',
                                  lastname='Prova',
                                  password='1234',
                                  date_of_birth='2001-01-01'
                              ),
                              follow_redirects=True)
        self.assertIn(b'Email already in use', reply.data)

        reply = self.app.post("/create_user",
                              data=dict(
                                  email="self.sender",
                                  firstname='Prova',
                                  lastname='Prova',
                                  pass_word='1234',
                                  date_of_birth='012001'
                              ),
                              follow_redirects=True)
        self.assertEqual(reply.status, '400 BAD REQUEST')

        self.logout()

    def test_content_filter(self):
        self.login(self.sender, "1234")
        reply = self.app.get('/userinfo/content_filter')
        self.assertIn(b'"active":false', reply.data)

        reply = self.app.get('/userinfo/content_filter/10')
        self.assertEqual(reply.status, '404 NOT FOUND')

        reply = self.app.put('/userinfo/content_filter/1', data=dict(active='false'))
        self.assertIn(b'"active":false', reply.data)

        reply = self.app.put('/userinfo/content_filter/1', data=dict(active='true'))
        self.assertIn(b'"active":true', reply.data)

        reply = self.app.put('/userinfo/content_filter/1', data=dict(active='false'))
        self.assertIn(b'"active":false', reply.data)

        reply = self.app.get('/userinfo/content_filter/1')
        self.assertIn(b'id', reply.data)

        self.logout()

    def test_message_view_content_filter(self):
        self.login(self.sender, "1234")

        msg_date = (datetime.datetime.now() - datetime.timedelta(days=10)).isoformat()
        message = dict(
            receiver=self.receiver,
            date=msg_date,
            text='test_message_view_content_filter_' + msg_date + ' merda')

        reply = self.app.post("/message/send",
                              data=message,
                              follow_redirects=True)
        self.assertEqual(reply.status, '200 OK')

        id = 0
        from monolith.app import app
        with app.app_context():
            msg = db.session.query(Message).filter(Message.text == message['text'], Message.delivered.is_(True)).first()
            count = 0
            while msg is None and count < 15:
                sleep(2)
                count += 1
                msg = db.session.query(Message).filter(
                    Message.text == message['text'], Message.delivered.is_(True)).first()
            id = msg.id

        reply = self.app.get("/message/" + str(id))
        self.assertEqual(reply.status, '200 OK')

        self.logout()

        self.login(self.receiver, '1234')

        reply = self.app.put('/userinfo/content_filter/1', data=dict(active='true'))
        self.assertIn(b'"active":true', reply.data)

        reply = self.app.get("/message/" + str(id))
        self.assertEqual(reply.status, '200 OK')
        self.assertIn(b'*****', reply.data)

        reply = self.app.get("/mailbox/received")
        self.assertEqual(reply.status, '200 OK')
        self.assertIn(b'*****', reply.data)

        reply = self.app.put('/userinfo/content_filter/1', data=dict(active='false'))
        self.assertIn(b'"active":false', reply.data)

        reply = self.app.get("/message/" + str(id))
        self.assertEqual(reply.status, '200 OK')
        self.assertIn(b'merda', reply.data)

        self.logout()

    def test_user_info(self):
        self.login(self.sender, "1234")

        reply = self.app.get("/userinfo")
        self.assertIn(b'Profile', reply.data)

        reply = self.app.post("/userinfo", data=dict(
            email=self.receiver,
            firstname='Prova_new',
            lastname='Prova_new',
            password='12345',
            date_of_birth='2001-01-01'
        ))
        self.assertIn(b"Email already in use", reply.data)

        reply = self.app.post("/userinfo", data=dict(
            email='new_' + self.sender,
            firstname='Prova_new',
            lastname='Prova_new',
            password='',
            date_of_birth='2001-01-01'
        ))
        self.assertIn(b"Prova_new", reply.data)

        reply = self.app.post("/userinfo", data=dict(
            email='new_' + self.sender,
            firstname='Prova_new',
            lastname='Prova_new',
            password='12345',
            date_of_birth='2001-01-01'
        ))

        self.logout()

        reply = self.login("new_" + self.sender, "12345")
        self.assertIn(b'Hi Prova_new', reply.data)

        reply = self.app.post("/userinfo", data=dict(
            email=self.sender,
            firstname='Prova_new',
            lastname='Prova_new',
            password='1234',
            date_of_birth='2001-01-01'
        ))

        self.logout()

    def test_user_report(self):
        self.login(self.sender, "1234")

        reply = self.app.get("/report/add")
        self.assertIn(b'Choose a user that you want to report', reply.data)

        reply = self.app.post("/report/add", data=dict(
            email=self.sender
        ), follow_redirects=True)
        self.assertIn(self.sender.encode('utf8'), reply.data)

        self.logout()

        self.login(self.receiver.encode('utf8'), "1234")

        reply = self.app.post("/report/add", data=dict(
            email=self.sender
        ), follow_redirects=True)
        self.assertIn(self.sender.encode('utf8'), reply.data)

        self.logout()

        reply = self.login(self.sender, "1234")
        self.assertIn(b"Login", reply.data)

        reply = self.app.post("/create_user",
                              data=dict(
                                  email=self.sender,
                                  firstname='Prova',
                                  lastname='Prova',
                                  password='1234',
                                  date_of_birth='2001-01-01'
                              ),
                              follow_redirects=True)
        self.assertIn(b'You have been suspended!', reply.data)
