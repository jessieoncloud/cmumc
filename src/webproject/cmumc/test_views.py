from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from cmumc.forms import *
from cmumc.models import *

from django.utils import timezone

class PageRenderingTest(TestCase):
	fixtures = ['modeldata.json']

	def setUp(self):
		self.client = Client()
		self.user_1 = User.objects.get(pk=1) # Siyang who has created 2 posts
		self.user_2 = User.objects.get(pk=2)

	def test_home(self):
		response = self.client.get(reverse('index'))
		self.assertEqual(response.status_code, 200)

	def test_stream(self):
		# Try to access without logging in, should be directed to login page
		response = self.client.get(reverse('stream'))
		self.assertEqual(response.status_code, 302)
		# Login and access
		login = self.client.login(username=self.user_1.username, password="1")
		self.assertTrue(login)
		response = self.client.get(reverse('stream'))
		self.assertEqual(response.status_code, 200)

	def test_mytask(self):
		# Try to access without logging in, should be directed to login page
		response = self.client.get(reverse('mytask'))
		self.assertEqual(response.status_code, 302)
		# Login and access
		self.client.login(username=self.user_1.username, password="1")
		response = self.client.get(reverse('mytask'))
		self.assertEqual(response.status_code, 200)

	def test_profile(self):
		# Try to access without logging in, should be directed to login page
		response = self.client.get(reverse('profile', args=(self.user_2.username,)))
		self.assertEqual(response.status_code, 302)
		# Login and access
		self.client.login(username=self.user_1.username, password=self.user_1.password)
		response = self.client.get(reverse('profile', args=(self.user_2.username,)))
		self.assertEqual(response.status_code, 200)
