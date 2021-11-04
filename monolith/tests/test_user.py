import unittest

from monolith.tests.test_base import TestBase


class TestApp(TestBase):
    def test_list_users(self):
        self.login(self.sender, "1234")
        self.app.get("/userinfo")
        self.logout()

    def test_user(self):
        self.login(self.sender, "1234")
        self.app.get("/users")
        self.logout()

    def test_recipients(self):
        self.login(self.sender, "1234")
        self.app.get("/message/recipients")
        self.logout()

    def test_create_user_page(self):
        self.login(self.sender, "1234")
        self.app.get("/create_user")
        self.logout()


