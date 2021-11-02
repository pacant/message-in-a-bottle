import unittest

from . import app, recipient, sender

class TestApp(unittest.TestCase):
    def test_list_users(self):
        app.get("/userinfo")

    def test_user(self):
        app.get("/users")

    def test_recipients(self):
        app.get("/message/recipients")

    def test_create_user_page(self):
        app.get("/create_user")


