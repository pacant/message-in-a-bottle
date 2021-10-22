import json
import unittest

from monolith.app import app as tested_app


class TestApp(unittest.TestCase):

    def test1_party(self):  # example
        app = tested_app.test_client()
        
        reply = app.post("/login",data=dict(email = "prova@example.it", password = "1234"))

        self.assertIn(b"Hi",reply.data)
