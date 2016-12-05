from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from cmumc.forms import *
from cmumc.models import *
from cmumc.views import *

# from unittest.mock import patch, MagicMock  # > python 3.4
from mock import patch, MagicMock  # < python 3.4
from django.utils import timezone
from django.test import RequestFactory

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
		self.client.login(username=self.user_1.username, password="1")
		response = self.client.get(reverse('profile', args=(self.user_2.username,)))
		self.assertEqual(response.status_code, 200)

class UserProfileTest(TestCase):
	fixtures = ['modeldata.json']

	def setUp(self):
		self.user = User.objects.get(pk=1)
		self.factory = RequestFactory()

	def test_get_update_profile(self):
		request = self.factory.get(reverse('edit_profile'))
		request.user = self.user
		response = update_profile(request)
		self.assertEqual(response.status_code, 200)

	@patch('cmumc.models.Profile.save', MagicMock(name="save"))
	def test_post_update_profile(self):
		data = {'phone': '+14125391111', 'year_in_school': 'Freshman', 'venmo': '@jessie'}
		request = self.factory.post(reverse('edit_profile'), data)
		request.user = self.user
		# Get the response
		# if successful, should be redirected to the profile page
		response = update_profile(request)
		self.assertEqual(response.status_code, 302)

	def test_get_mode(self):
		request = self.factory.get(reverse('mode'))
		request.user = self.user
		response = update_profile(request)
		self.assertEqual(response.status_code, 200)

	@patch('cmumc.models.Profile.save', MagicMock(name="save"))
	def test_post_mode(self):
		data = {'mode': 'H'}
		request = self.factory.post(reverse('mode'), data)
		request.user = self.user
		# Get the response
		# if successful, should be redirected to the profile page
		response = mode(request)
		self.assertEqual(response.status_code, 302)

	@patch('cmumc.models.Profile.save', MagicMock(name="save"))
	def test_post_switch(self):
		data = {'mode_username': self.user.username}
		request = self.factory.post(reverse('switch'), data)
		request.user = self.user
		# Get the response
		response = switch(request)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.usertype, 'R')


class PostManagementTest(TestCase):
	fixtures = ['modeldata.json']

	def setUp(self):
		self.user = User.objects.get(pk=1)
		self.factory = RequestFactory()

	def test_send_post(self):
		data = {'title': 'post_title', 'description': 'post_description', 'category': 'Driving',
                'date': '12/25/2099', 'time': '06:25', 'price': 12.0}
		request = self.factory.post(reverse('create'), data)
		request.user = self.user
		# Get the response
		response = send_post(request)
		self.assertEqual(response.status_code, 302)
		self.assertTrue(response.content.find())

	