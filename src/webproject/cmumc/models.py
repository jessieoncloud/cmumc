from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    created_user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_type = models.BooleanField()
    category = models.CharField(max_length=1, choices=POST_CATEGORY_CHOICES)
    created_time = models.DateTimeField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=100, default="", blank=True)
    price = models.IntegerField()
    status = models.CharField(max_length=10)
    accept_list = models.ManyToManyField(User)

    class Meta:
        ordering = ['-created_time']

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read = models.BooleanField()
    content = models.TextField(max_length=1000)

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_type = models.BooleanField()
    score = models.IntegerField()
    review = models.TextField(max_length=400, default="", blank=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone = models.CharField(max_length=15)
    user_type = models.BooleanField()
    activation_key = models.CharField(max_length=255)

    intro = models.TextField(max_length=420, default="", blank=True)
    photo = models.ImageField(upload_to="profile_photo", blank=True)
    venmo = models.CharField(max_length=20,default="", blank=True)



