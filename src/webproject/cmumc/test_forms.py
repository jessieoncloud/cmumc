from django.test import TestCase
from cmumc.forms import *
from django import forms
from django.contrib.auth.models import User
from cmumc.models import *

class RegistrationFormTestCase(TestCase):
    def test_valid_form(self):
        data = {'first_name': 'Jessie', 'last_name': 'Bar', 'user_name': 'jessie',
                'email': 'jessie@andrew.cmu.edu', 'password1': '0', 'password2': '0'}
        form = RegistrationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_null_field_form(self):
        data = {'first_name': 'Jessie', 'last_name': '', 'user_name': 'jessie',
                'email': 'jessie@andrew.cmu.edu', 'password1': '0', 'password2': '0'}
        form = RegistrationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_password_match(self):
        data = {'first_name': 'Jessie', 'last_name': '', 'user_name': 'jessie',
                'email': 'jessie@andrew.cmu.edu', 'password1': '0', 'password2': '1'}
        form = RegistrationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_username_unique(self):
        new_user = User.objects.create(first_name='Jessie', last_name='Bar', username='jessie',
                                       email='jessie@andrew.cmu.edu', password='0')
        data = {'first_name': 'Vita', 'last_name': 'Chen', 'user_name': new_user.username,
                'email': new_user.email, 'password1': new_user.password, 'password2': new_user.password}
        form = RegistrationForm(data=data)
        self.assertFalse(form.is_valid())

    # def test_email_format(self):
    #     data = {'first_name': 'Jessie', 'last_name': 'Bar', 'user_name': 'jessie',
    #             'email': 'jessie@andrew.usc.edu', 'password1': '0', 'password2': '0'}
    #     form = RegistrationForm(data=data)
    #     self.assertFalse(form.is_valid)
    #     # ## We run is_valid() and expect False
    #     # self.failIf(form.is_valid())
    #     # # check for the error
    #     # print(form.errors)
    #     # self.assertIn(u'Please enter a valid CMU email address', form.errors['__all__'])

class UserFormTestCase(TestCase):
    def test_valid_form(self):
        data = {'first_name': 'Jessie', 'last_name': 'Bar'}
        form = UserForm(data=data)
        self.assertTrue(form.is_valid())

    def test_optional_field_form(self):
        data = {'first_name': 'Jessie', 'last_name': ''}
        form = UserForm(data=data)
        self.assertTrue(form.is_valid())

class PostFormTestCase(TestCase):
    def test_valid_form(self):
        data = {'title': 'post_title', 'description': 'post_description', 'category': 'Driving',
                'date': '12/25/2099', 'time': '06:25', 'price': 12.0}
        form = PostForm(data=data)
        self.assertTrue(form.is_valid())

    def test_date_form(self):
        data = {'title': 'post_title', 'description': 'post_description', 'category': 'Driving',
                'date': '10/25/2016', 'time': '06:25', 'price': 12.0}
        form = PostForm(data=data)
        self.assertFalse(form.is_valid())

    def test_null_field_form(self):
        data = {'title': 'post_title', 'description': 'post_description', 'category': 'Driving',
                'date': '10/25/2016', 'time': '', 'price': 12.0}
        form = PostForm(data=data)
        self.assertFalse(form.is_valid())

class ModeFormTestCase(TestCase):
    def test_valid_form(self):
        data = {'mode': 'H'}
        form = ModeForm(data=data)
        self.assertTrue(form.is_valid())

    def test_null_field_form(self):
        data = {'mode': ''}
        form = ModeForm(data=data)
        self.assertFalse(form.is_valid())

class ProfileFormTestCase(TestCase):
    def test_valid_form(self):
        data = {'phone': '+14125391111', 'year_in_school': 'Freshman', 'venmo': '@jessie'}
        form = ProfileForm(data=data)
        self.assertTrue(form.is_valid())

    def test_null_field_form(self):
        data = {'phone': '+14125391111', 'year_in_school': 'Freshman', 'venmo': ''}
        form = ProfileForm(data=data)
        self.assertFalse(form.is_valid())

    def test_phone_field_form(self):
        data = {'phone': '+4121111111', 'year_in_school': 'Freshman', 'venmo': '@jessie'}
        form = ProfileForm(data=data)
        self.assertFalse(form.is_valid())

class MessageFormTestCase(TestCase):
    def test_valid_form(self):
        data = {'body': 'message body'}
        form = MessageForm(data=data)
        self.assertTrue(form.is_valid())

    def test_null_field_form(self):
        data = {'body': ''}
        form = MessageForm(data=data)
        self.assertFalse(form.is_valid())

class SearchFormTestCase(TestCase):
    def test_valid_form(self):
        data = {'keyword': 'search string'}
        form = SearchForm(data=data)
        self.assertTrue(form.is_valid())

    def test_null_field_form(self):
        data = {'keyword': ''}
        form = SearchForm(data=data)
        self.assertFalse(form.is_valid())

class RateFormTestCase(TestCase):
    def test_valid_form(self):
        data = {'created_time': '2006-10-25 14:30:59', 'rated_user_type': 'H', 'score': 3.0, 'review': 'rated review'}
        form = RateForm(data=data)
        self.assertTrue(form.is_valid())

    def test_null_field_form(self):
        data = {'created_time': '2006-10-25 14:30:59', 'rated_user_type': 'H', 'score': '', 'review': 'rated review'}
        form = RateForm(data=data)
        self.assertFalse(form.is_valid())

    def test_score_range(self):
        data = {'created_time': '2006-10-25 14:30:59', 'rated_user_type': 'H', 'score': 6.0, 'review': 'rated review'}
        form = RateForm(data=data)
        self.assertFalse(form.is_valid())

