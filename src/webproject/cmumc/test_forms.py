from django.test import TestCase
from cmumc.forms import *

from django import forms
from django.contrib.auth.models import User
from cmumc.models import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class RegistrationFormTestCase(TestCase):
    # def setUp(self):
    #     self.new_user = User.objects.create_user(first_name='Jessie', last_name='Bar', username='jessie',
    #                                    email='jessie@andrew.cmu.edu', password='0')
    def test_valid_form(self):
        new_user = User.objects.create(first_name='Jessie', last_name='Bar', username='jessie',
                                            email='jessie@andrew.cmu.edu', password='0')
        data = {'first_name': new_user.first_name, 'last_name': new_user.last_name, 'user_name': new_user.username,
                'email': new_user.email, 'password1': new_user.password, 'password2': new_user.password}
        form = RegistrationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_null_field_form(self):
        new_user = User.objects.create(first_name='Jessie', last_name='', username='jessie',
                                            email='jessie@andrew.cmu.edu', password='0')
        data = {'first_name': new_user.first_name, 'last_name': new_user.last_name, 'user_name': new_user.username,
                'email': new_user.email, 'password1': new_user.password, 'password2': new_user.password}
        form = RegistrationForm(data=data)
        self.assertFalse(form.is_valid())

    # def test_password_match(self):
    #     new_user = User.objects.create(first_name='Jessie', last_name='Bar', username='jessie',
    #                                    email='jessie@andrew.cmu.edu', password='0')
    #     data = {'first_name': new_user.first_name, 'last_name': new_user.last_name, 'user_name': new_user.username,
    #             'email': new_user.email, 'password1': new_user.password, 'password2': '1'}
    #     form = RegistrationForm(data=data)
    #     ## do not know how to test
    #     with self.assertRaisesRegexp(ValidationError, "Passwords do not match"):
    #         pass


    # def test_username_unique(self):
    #     data = {'first_name': 'Vita', 'last_name': 'Chen', 'user_name': new_user.username,
    #             'email': new_user.email, 'password1': new_user.password, 'password2': new_user.password}
    #     form = RegistrationForm(data=data)
    #     self.assertIn('already taken', form.errors['username'][0])

    # def test_email_format(self):
    #     new_user = User.objects.create(first_name='Jessie', last_name='Bar', username='jessie',
    #                                    email='jessie@andrew.usc.edu', password='0')
    #     data = {'first_name': new_user.first_name, 'last_name': new_user.last_name, 'user_name': new_user.username,
    #             'email': new_user.email, 'password1': new_user.password, 'password2': new_user.password}
    #     form = RegistrationForm(data=data)
    #     self.assertTrue(form.is_valid)
    #     self.assertIsNone(form.clean_email())
    #     # ## We run is_valid() and expect False
    #     # self.failIf(form.is_valid())
    #     ## check for the error
    #     ## self.assertIn(u'Please enter a valid CMU email address', form.errors['__all__'])
