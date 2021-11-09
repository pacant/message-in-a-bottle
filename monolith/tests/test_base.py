import unittest

from monolith.app import app as tested_app
from monolith.database import db, User, Message, ContentFilter
from monolith.views.messages import draft


class TestBase(unittest.TestCase):
    tested_app.config['WTF_CSRF_ENABLED'] = False
    app = tested_app.test_client()

    def test_default_content_filter(self):
        with tested_app.app_context():
            id = db.session.query(ContentFilter).filter(ContentFilter.name == 'Default').first().id
            self.assertEqual(int(id), 1)

    sender = "prova@gmail.com"
    receiver = "prova1@gmail.com"
    other = "prova2@gmail.com"

    def register(self, email, firstname, lastname, password, dateofbirth):
        return self.app.post("/create_user",
                             data=dict(
                                 email=email,
                                 firstname=firstname,
                                 lastname=lastname,
                                 password=password,
                                 date_of_birth=dateofbirth
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
    
    def test_user_creation(self):
        self.register(self.sender, "Prova", "Prova", "1234", "2001-01-01")
        self.register(self.receiver, "Prova", "Prova", "1234", "2001-01-01")
        self.register(self.other, "Prova", "Prova", "1234", "2001-01-01")
