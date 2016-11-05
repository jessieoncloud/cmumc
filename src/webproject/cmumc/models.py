from django.db import models
from django.contrib.auth.models import User

UserType = (
    ('H', 'Helper'),
    ('R', 'Receiver'),
)

class Post(models.Model):
    created_user = models.ForeignKey(User, related_name="created", on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=UserType)
    category = models.CharField(max_length=20)
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
    user_type = models.CharField(max_length=10, choices=UserType)
    score = models.IntegerField()
    review = models.TextField(max_length=400, default="", blank=True)

class Profile(models.Model):
    YEAR_IN_SCHOOL_CHOICES = (
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone = models.CharField(max_length=15)
    user_type = models.CharField(max_length=10, choices=UserType)
    activation_key = models.CharField(max_length=255)
    year_in_school = models.CharField(
        max_length=2,
        choices=YEAR_IN_SCHOOL_CHOICES,
        default='FR',
    )
    major = models.CharField(max_length=255, default="", blank=True)
    bio = models.TextField(max_length=420, default="", blank=True)
    photo = models.ImageField(upload_to="profile_photo", blank=True)
    venmo = models.CharField(max_length=20, default="", blank=True)

    def is_upperclass(self):
        return self.year_in_school in (self.JUNIOR, self.SENIOR)



