from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from geoposition.fields import GeopositionField

UserType = (
    ('H', 'Helper'),
    ('R', 'Receiver'),
)

StatusType = (
    ('NC', 'NeedConfirmation'),
    ('I', 'InProgress'),
    ('A', 'Available'),
    ('C', 'Complete'),
)

PostCategory = (
    ('Driving', 'Driving'),
    ('Tutoring', 'Tutoring'),
    ('Others', 'Others'),
)

TaskStatusType = (
    ('I', 'InProgress'),
    ('C', 'Complete'),
    ('R', 'Rated'),
)

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=400)
    created_user = models.ForeignKey(User, related_name="created", on_delete=models.CASCADE)
    post_type = models.CharField(max_length=10, choices=UserType)
    category = models.CharField(max_length=20, choices=PostCategory)
    created_time = models.DateTimeField(auto_now_add=True)
    date = models.DateField()
    time = models.TimeField()
    location = GeopositionField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, default="A", choices=StatusType)
    deleted = models.BooleanField(default=False)
    accept_list = models.ManyToManyField(User)
    post_photo = models.ImageField(upload_to="post-photo", blank=True)

    @staticmethod
    def get_all_posts():
        return Post.objects.all()

    @staticmethod
    def get_user_posts(created_user):
        return Post.objects.filter(created_user=created_user).filter(deleted=False)

    @staticmethod
    def get_post_list_data(post_list):
        result = []
        for post in post_list:
            temp = {}
            temp['post_id'] = post.post_id
            # temp['location'] = post.location
            temp['date'] = post.date
            temp['username'] = post.created_user.username
            temp['time'] = post.time
            temp['price'] = post.price
            temp['title'] = post.title
            result.append(temp)
        return result


    class Meta:
        ordering = ['-created_time']

class Task(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, primary_key=True)
    helper = models.ForeignKey(User, on_delete=models.CASCADE, related_name="helper")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    helper_status = models.CharField(max_length=10, choices=TaskStatusType, default='I')
    receiver_status = models.CharField(max_length=10, choices=TaskStatusType, default='I')
    task_status = models.CharField(max_length=10, choices=TaskStatusType, default='I')

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read = models.BooleanField()
    content = models.TextField(max_length=1000)

class Rating(models.Model):
    created_user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    rated_user_type = models.CharField(max_length=10, choices=UserType)
    score = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    review = models.TextField(max_length=400, default="Thank you very much.", blank=True)

    class Meta:
        ordering = ['-created_time']

class Profile(models.Model):
    YEAR_IN_SCHOOL_CHOICES = (
        ('Freshman', 'Freshman'),
        ('Sophomore', 'Sophomore'),
        ('Junior', 'Junior'),
        ('Senior', 'Senior'),
        ('Graduate', 'Graduate'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone = PhoneNumberField()
    user_type = models.CharField(max_length=10, choices=UserType)
    activation_key = models.CharField(max_length=255)
    year_in_school = models.CharField(
        max_length=15,
        choices=YEAR_IN_SCHOOL_CHOICES,
        default='Freshman'
    )
    major = models.CharField(max_length=255, default="", blank=True)
    bio = models.TextField(max_length=420, default="", blank=True)
    photo = models.ImageField(upload_to="profile-photo", blank=True)
    venmo = models.CharField(max_length=20, default="")
    helper_score = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    receiver_score = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)


