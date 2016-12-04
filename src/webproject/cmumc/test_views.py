from django.test import TestCase
from django.test import Client
import unittest
from .forms import *

# class Setup_Class(TestCase):
#     def setUp(self):
#         self.user = User.objects.create(first_name='Vita', last_name='Bar', username='vita',
#                                             email='jessie@andrew.cmu.edu', password='0')
#
# class User_Views_Test(SetUp_Class):
#     def test_home_view(self):
#         user_login = self.client.login(email="vita@andrew.cmu.edu", password="0")
#         self.assertTrue(user_login)
#         response = self.client.get("/")
#         self.assertEqual(response.status_code, 302)

class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_stream(self):
        # Issue a GET request.
        response = self.client.get('/cmumc/stream')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

