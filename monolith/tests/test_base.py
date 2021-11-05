import unittest

from monolith.app import app as tested_app
from monolith.database import db, User, Message
from monolith.views.messages import draft


class TestBase(unittest.TestCase):
    tested_app.config['WTF_CSRF_ENABLED'] = False
    app = tested_app.test_client()

    sender = "prova@gmail.com"
    receiver = "prova1@gmail.com"

    def register(self, email, firstname, lastname, password, dateofbirdth):
        return self.app.post("/create_user",
                             data=dict(
                                 email=email,
                                 firstname=firstname,
                                 lastname=lastname,
                                 password=password,
                                 dateofbirth=dateofbirdth
                             ),
                             follow_redirects=True)

    def login(self, email, password):
        return self.app.post("/login",
                             data=dict(
                                 email=email,
                                 password=password
                             ),
                             follow_redirects=True)

    def unregister(self):
        return self.app.post("/delete_user")

    def logout(self):
        return self.app.get("/logout")

    app.post("/create_user",
             data=dict(
                 email=sender,
                 firstname="Prova",
                 lastname="Prova",
                 password="1234",
                 dateofbirth="01/01/2001"
             ),
             follow_redirects=True)

    app.post("/create_user",
             data=dict(
                 email=receiver,
                 firstname="Prova",
                 lastname="Prova",
                 password="1234",
                 dateofbirth="01/01/2001"
             ),
             follow_redirects=True)
