from django.test import TestCase, Client
from cmumc.models import *
from django.contrib.auth.models import User
from model_mommy import mommy

class PostTestMommy(TestCase):
    fixtures = ['modeldata.json']
    def setUp(self):
        super(PostTestCase, self).setUp()
        self.user_1 = User.objects.get(pk=1)
        self.user_2 = User.objects.get(pk=2)

    def test_post_creation_mommy(self):
        new_post = mommy.make('cmumc.Post')
        self.assertTrue(isinstance(new_post, Post))

    def test_create_post_model(self):
        self.assertTrue(Post.objects.all().count() == 2)
        new_post = Post(title="test", description="test post", created_user=self.user_1, post_type="H",
                        category="Others", created_time="2016-12-04T14:24:51.762Z",
                        date="2016-12-05", time="09:00:00", price="15.00", status="A",
                        deleted="False")
        new_post.save()
        self.assertTrue(Post.objects.all().count() == 3)
        self.assertTrue(Post.objects.filter(title__contains='test'))

    def test_get_all_post(self):
        self.assertFalse(Post.objects.all().count() == 0)
        self.assertTrue(Post.objects.all().count() == 2)

    def test_get_user_posts(self):
        self.assertFalse(Post.objects.filter(created_user=self.user_2).filter(deleted=False))
        self.assertTrue(Post.objects.filter(created_user=self.user_1).filter(deleted=False))
        # Delete all posts and check this method again
        Post.objects.filter(created_user=self.user_1).delete()
        self.assertFalse(Post.objects.filter(created_user=self.user_1).filter(deleted=False))

    def tearDown(self):
        del self.user_1
        del self.user_2

class TaskTestMommy(TestCase):
    def test_post_creation_mommy(self):
        new_task = mommy.make('cmumc.Task')
        self.assertTrue(isinstance(new_task, Task))

class NotificationTestMommy(TestCase):
    def test_post_creation_mommy(self):
        new_notification = mommy.make('cmumc.Notification')
        self.assertTrue(isinstance(new_notification, Notification))

class RatingTestMommy(TestCase):
    def test_rating_creation_mommy(self):
        new_rating = mommy.make('cmumc.Rating')
        self.assertTrue(isinstance(new_rating, Rating))

class ProfileTestCase(TestCase):
    def test_profile_creation_mommy(self):
        user = User(first_name="test", last_name="test", username="testuser")
        new_profile = Profile(user=user, phone="+14122225678", user_type="H", activation_key="activate",
                              year_in_school="Freshman", venmo="venmo")
        self.assertTrue(isinstance(new_profile, Profile))




