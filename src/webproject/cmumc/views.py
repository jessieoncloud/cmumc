from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.core.urlresolvers import reverse

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from django.db import transaction

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator

from mimetypes import guess_type
from cmumc import *
from cmumc.models import *
from cmumc.forms import *

from django.core import serializers
import json

##twilio
from twilio import TwilioRestException
from twilio.rest import TwilioRestClient

import datetime
from datetime import date
from datetime import timedelta
from django.utils import timezone
import json
import time
from django.core.serializers.json import DjangoJSONEncoder

##global variables
account_sid = "AC9e5aa3ee46da9ab37b1d6253f7bd3c47" # Your Account SID from www.twilio.com/console
auth_token  = "02c39149b58d384088214ef900b52c0f"  # Your Auth Token from www.twilio.com/console
##test
#account_sid = "AC62277389af8bc0a7fc1e0ab6d0c63994"
#auth_token  = "3669b7ba50772b26d37983af9522d862"

twilio_number = "+14126936893"
client = TwilioRestClient(account_sid, auth_token)

# def contact_test(request, post_id):
#     context = {}
#     context['msgs'] = "hello"
#     return render(request, 'cmumc/contact.html', context)

# Create your views here.
def home(request):
    return render(request, 'cmumc/index.html', {})

@login_required
def stream(request):
    context = {}
    user_profile = get_object_or_404(Profile, user=request.user)
    if user_profile.user_type == 'H':
        all_posts = Post.objects.all().filter(post_type='R').filter(deleted=False)
    elif user_profile.user_type == 'R':
        all_posts = Post.objects.all().filter(post_type='H').filter(deleted=False)

    context['posts'] = all_posts
    return render(request, 'cmumc/stream.html', context)

@login_required
def view_post(request, post_id):
    context = {}
    errors = []
    context['errors'] = errors
    context['accepted'] = False
    user_profile = get_object_or_404(Profile, user=request.user)
    post_item = get_object_or_404(Post, post_id=post_id)
    if post_item.deleted:
        errors.append("The post has been deleted")
        return render(request, 'cmumc/error.html', context)
    else:
        context['post'] = post_item
        # Check if the usertype and post type is correct
        if (user_profile.user_type == post_item.post_type and request.user != post_item.created_user):
            return redirect('stream')
        if len(post_item.accept_list.filter(username=request.user.username)) != 0:
            context['accepted'] = True
        return render(request, 'cmumc/view_post.html', context)

@login_required
@transaction.atomic
def send_post(request):
    context = {}
    user_profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'GET':
        context['form'] = PostForm()
        context['profile'] = user_profile
        return render(request, 'cmumc/create_post.html', context)

    if request.user.is_authenticated:
        new_post = Post(created_user=request.user, post_type=user_profile.user_type)
        form = PostForm(request.POST, request.FILES, instance=new_post)
        context['form'] = form
        context['profile'] = user_profile

        if not form.is_valid():
            return render(request, 'cmumc/create_post.html', context)

        form.save()

        return redirect('stream')
    else:
        return render(request, 'cmumc/login.html', context)

# return all tasks related to the current user
@login_required
def mytask(request):
    context = {}
    user_item = get_object_or_404(User, username=request.user.username)
    user_profile = get_object_or_404(Profile, user=request.user)
    user_post = Post.objects.filter(created_user=request.user).filter(deleted=False).filter(post_type=user_profile.user_type)
    # check for bugs
    accept_post = user_item.post_set.filter(deleted=False).exclude(post_type=user_profile.user_type)
    posts = user_post | accept_post
    context['posts'] = posts.distinct()

    return render(request,'cmumc/mytask.html', context)

def notification(post_id):
    post_item = get_object_or_404(Post, post_id=post_id)
    if post_item.status == 'I':
        msg_body = "Your post \"" + post_item.title + "\" is now in progress."
    elif post_item.status == 'C':
        msg_body = "Your post \"" + post_item.title + "\" is now complete! Please rate this task on CMUMC."

    task_item = get_object_or_404(Task, post=post_item)
    recipient_list = [task_item.helper, task_item.receiver]
    for recipient in recipient_list:
        to_profile = Profile.objects.get(user=recipient)
        try:
            message = client.messages.create(body=msg_body,
                                             #to="+14125396418",  # Replace with your phone number
                                             to=str(to_profile.phone),
                                            from_=twilio_number)
                                             #from_="+15005550006")  # Replace with your Twilio number
            success = True
        except TwilioRestException as e:
            print(e)
            success = False

    return success


@login_required
@transaction.atomic
def edit_post(request, post_id):
    context = {}
    errors = []
    context['errors'] = errors
    post_item = get_object_or_404(Post, post_id=post_id)
    context['post'] = post_item
    if post_item.created_user != request.user:
        return redirect('stream')
    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES, instance=post_item)
        context['form'] = post_form
        if post_form.is_valid():
            post_form.save()
            return redirect('viewPost', post_id = post_id)
        else:
            print(post_form.errors)
            return render(request, 'cmumc/edit_post.html', context)
    else:
        post_form = PostForm(instance=post_item)
    return render(request, 'cmumc/edit_post.html', {'form': post_form, 'post':post_item})

@login_required
@transaction.atomic
def delete_post(request, post_id):
    context = {}
    post_item = get_object_or_404(Post, post_id=post_id)
    if post_item.created_user != request.user:
        return redirect('stream')
    post_item.deleted = True
    post_item.save()
    return render(request, 'cmumc/stream.html', context)

@login_required
@transaction.atomic
def accept_post(request, post_id):
    context = {}
    errors = []
    context['errors'] = errors
    user_item = get_object_or_404(User, username=request.user.username)
    user_profile = get_object_or_404(Profile, user=request.user)
    user_post = Post.objects.filter(created_user=request.user).filter(deleted=False).filter(
        post_type=user_profile.user_type)
    accept_post = user_item.post_set.filter(deleted=False).exclude(post_type=user_profile.user_type)
    posts = user_post | accept_post
    context['posts'] = posts.distinct()
    post_item = get_object_or_404(Post, post_id=post_id)

    if post_item.status == 'I' or post_item.status == 'C':
        errors.append("You cannot accept for this post")
        return render(request, 'cmumc/error.html', context)
    else:
        post_item.accept_list.add(request.user)
        post_item.status = 'NC'
        post_item.save()

        return render(request, 'cmumc/mytask.html', context)

@login_required
def view_accept_list(request, post_id):
    context = {}
    post_item = get_object_or_404(Post, post_id=post_id)
    accept_list = post_item.accept_list.all()
    context['accept_list'] = accept_list
    user_item = get_object_or_404(User, username=request.user.username)
    user_profile = get_object_or_404(Profile, user=request.user)
    user_post = Post.objects.filter(created_user=request.user).filter(deleted=False).filter(
        post_type=user_profile.user_type)
    accept_post = user_item.post_set.filter(deleted=False).exclude(post_type=user_profile.user_type)
    posts = user_post | accept_post
    context['posts'] = posts.distinct()

    return render(request, 'cmumc/mytask.html', context)

##choose one user from accept_list to accept
@login_required
@transaction.atomic
def accept(request, post_id):
    context = {}
    errors = []
    context['errors'] = errors
    message = []
    context['message'] = message
    if 'requester' in request.POST and request.POST['requester']:
        username = request.POST['requester']
    else:
        errors.append("Request user does not exist")
        return render(request, 'cmumc/errors.html', context)

    post_item = get_object_or_404(Post, post_id=post_id)
    user_item = get_object_or_404(User, username=request.user.username)
    user_profile = get_object_or_404(Profile, user=request.user)
    user_post = Post.objects.filter(created_user=request.user).filter(deleted=False).filter(
        post_type=user_profile.user_type)
    accept_post = user_item.post_set.filter(deleted=False).exclude(post_type=user_profile.user_type)
    posts = user_post | accept_post
    context['posts'] = posts.distinct()

    try:
        accepted_user = post_item.accept_list.get(username=username)
    except:
        errors.append("The user does not exist in the accept list of the post")
        return render(request, 'cmumc/errors.html', context)

    post_item.status = 'I'

    if post_item.post_type == 'H':
        new_task = Task(post=post_item,
                        helper=request.user,
                        receiver=accepted_user)
    else:
        new_task = Task(post=post_item,
                        helper=accepted_user,
                        receiver=request.user)
    new_task.save()
    post_item.save()
    sent = notification(post_id)
    if sent:
        message.append("Your message has been sent")
    else:
        message.append("Your message failed to send")
    return render(request, 'cmumc/mytask.html', context)

@login_required
@transaction.atomic
def complete(request, post_id):
    context = {}
    errors = []
    context['errors'] = errors
    message = []
    context['message'] = message
    post_item = get_object_or_404(Post, post_id=post_id)
    user_item = get_object_or_404(User, username=request.user.username)
    user_profile = get_object_or_404(Profile, user=request.user)
    user_post = Post.objects.filter(created_user=request.user).filter(deleted=False).filter(
        post_type=user_profile.user_type)
    accept_post = user_item.post_set.filter(deleted=False).exclude(post_type=user_profile.user_type)
    posts = user_post | accept_post
    context['posts'] = posts.distinct()

    if not post_item.status == 'I':
        errors.append("This post status is not in progress and you cannot complete it")
        return render(request, 'cmumc/error.html', context)

    try:
        task_item = Task.objects.get(post=post_item)
    except:
        task_item = Task(post=post_item)
    if request.user == task_item.helper:
        task_item.helper_status = 'C'
    else:
        task_item.receiver_status = 'C'
    task_item.save()
    if task_item.helper_status == 'C' and task_item.receiver_status == 'C':
        task_item.task_status = 'C'
        task_item.save()
        post_item.status = 'C'
        post_item.save()
        sent = notification(post_id)
        if sent:
            message.append("Your message has been sent")
        else:
            message.append("Your message failed to send")
        return render(request, 'cmumc/mytask.html', context)
    else:
        return render(request, 'cmumc/mytask.html', context)

@login_required
def mode(request):
    context = {}
    if request.method == 'GET':
        context['helper_form'] = ModeForm()
        context['receiver_form'] = ModeForm()
        return render(request, 'cmumc/mode.html', context)

    form = ModeForm(request.POST)
    ##weird bug, if you remove print, it cannot work
    print(form)
    user_profile = get_object_or_404(Profile, user=request.user)
    modename = form.cleaned_data.get('mode')
    user_profile.user_type = modename
    user_profile.save()
    return redirect('stream')

# Ajax switch mode
@login_required
def switch(request):
    # Validation
    if request.method == 'GET':
        return redirect('stream')
    if not 'mode_username' in request.POST or not request.POST['mode_username']:
        return redirect('stream')
    user = get_object_or_404(User, username=request.POST['mode_username'])
    user_profile = get_object_or_404(Profile, user=user.id)
    if user_profile.user_type == 'H':
        user_profile.user_type = 'R'
    else:
        user_profile.user_type = 'H'
    user_profile.save()
    response = json.dumps({"usertype": user_profile.user_type})
    return HttpResponse(response, content_type="application/json")

@login_required
def profile(request, user_name):
    context = {}
    user_item = get_object_or_404(User, username=user_name)
    try:
        user_profile = Profile.objects.get(user=user_item)
    except:
        user_profile = Profile(user=user_item)
    context['profile'] = user_profile
    user_post = Post.get_user_posts(user_item).filter(deleted=False)
    context['posts'] = user_post
    ##render reviews and ratings
    helper_task = Task.objects.filter(helper=user_item)
    context['helper_task'] = helper_task
    receiver_task = Task.objects.filter(receiver=user_item)
    context['receiver_task'] = receiver_task
    return render(request, 'cmumc/profile.html', context)

@login_required
def get_photo(request, user_name):
    user_item = get_object_or_404(User, username=user_name)
    profile = get_object_or_404(Profile, user=user_item)
    if not profile.photo:
        raise Http404

    content_type = guess_type(profile.photo.name)
    return HttpResponse(profile.photo, content_type=content_type)

@login_required
def get_post_photo(request, post_id):
    post_item = get_object_or_404(Post, post_id=post_id)
    if not post_item.post_photo:
        if (post_item.category == "Driving"):
            post_item.post_photo = "post-photo/driving.png"
        elif (post_item.category == "Tutoring"):
            post_item.post_photo = "post-photo/tutoring.png"
        else:
            post_item.post_photo = "post-photo/others.jpg"
        post_item.save()

    content_type = guess_type(post_item.post_photo.name)
    return HttpResponse(post_item.post_photo, content_type=content_type)

@login_required
@transaction.atomic
def update_profile(request):
    context = {}
    try:
        user_profile = Profile.objects.get(user=request.user)
    except:
        user_profile = Profile(user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        context['profile_form'] = profile_form
        context['user_form'] = user_form
        if all([user_form.is_valid(), profile_form.is_valid()]):
            print("update_profile successfully")
            user_form.save()
            profile_form.save()
            print(profile_form)
            return redirect('profile', user_name=request.user.username)
        else:
            print("update_profile fails")
            print(profile_form.errors)
            print(user_form.errors)
            return render(request, 'cmumc/edit_profile.html', context)
    else:
        print("update profile get")
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=user_profile)
    return render(request, 'cmumc/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@transaction.atomic
def register(request):
    context = {}

    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'cmumc/registration.html', context)

    form = RegistrationForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'cmumc/registration.html', context)

    ## create new_user
    new_user = User.objects.create_user(username=form.cleaned_data['user_name'], \
                    first_name=form.cleaned_data['first_name'], \
                    last_name=form.cleaned_data['last_name'], \
                    password=form.cleaned_data['password1'],\
                    email=form.cleaned_data['email'])
    new_user.is_active = False
    new_user.save()

    token = default_token_generator.make_token(new_user)

    user_profile = Profile(user=new_user, photo="profile-photo/avatar.png", activation_key=token)
    user_profile.save()

    email_body = """
Welcome to cmumc! Please click the link below to verify your email address and complete the registration of your account:
http://%s%s
    """ % (request.get_host(),
           reverse('confirm', args=(new_user.username, token)))

    send_mail(subject="Verify your email account",
              message=email_body,
              from_email="siyangli@andrew.cmu.edu",
              recipient_list=[new_user.email])

    context['email'] = form.cleaned_data['email']
    return render(request, 'cmumc/needs-confirmation.html', context)

@transaction.atomic
def confirm_register(request, user_name, token):
    try:
        user_item = User.objects.get(username=user_name)
        user_profile = Profile.objects.get(user=user_item)
        if user_profile.activation_key == token:
            user_item.is_active = True
            user_item.save()
            new_user = authenticate(username=user_item.username, \
                            password=user_item.password)
            login(request, new_user)
        return redirect('index')
    except:
        return redirect('index')

##messaging module
def send_message(request, post_id):
    context = {}
    msgs = []
    context['msgs'] = msgs
    context['form'] = MessageForm()
    post_item = get_object_or_404(Post, post_id=post_id)
    context['post'] = post_item
    if request.method == "GET":
        return render(request, 'cmumc/contact2.html', context)
    from_profile = get_object_or_404(Profile, user=request.user)
    to_user = post_item.created_user
    to_profile = get_object_or_404(Profile, user=to_user)

    form = MessageForm(request.POST)

    context['form'] = form

    if not form.is_valid():
        msgs.append("Your message is not valid.")
        return render(request, 'cmumc/contact.html', context)
    body = form.cleaned_data['body']

    msg_body = "Message from CMUMC.\n\nYour post \"" + post_item.title + "\" has been viewed by " + from_profile.user.username + ".\n" \
            + from_profile.user.username + " would like to send you a message:\n\n" + body + "\n \n" \
            + "You can contact him/her by " + str(from_profile.phone)
    try:
        message = client.messages.create(body=msg_body,
                                         #to="+14125396418",  # Replace with your phone number
                                         to=str(to_profile.phone),
                                        from_=twilio_number)
                                         #from_="+15005550006")  # Replace with your Twilio number
        msgs.append("Your message has been sent sucessfully")
    except TwilioRestException as e:
        print(e)
        msgs.append("Sent message failed, please try again")
    return render(request, 'cmumc/contact.html', context)

@login_required
def search_post(request):
    print(request.POST)
    context = {}
    messages = []
    context['messages'] = messages
    user_profile = get_object_or_404(Profile, user=request.user)
    form = SearchForm(request.POST)

    if not form.is_valid():
        messages.append("Invalid search")
        context['form'] = form
        return render(request, 'cmumc/stream.html', context)
    
    keyword = form.cleaned_data['keyword']
    posts_title = Post.objects.filter(deleted=False).exclude(post_type=user_profile.user_type).filter(title__icontains=keyword)
    posts_description = Post.objects.filter(deleted=False).exclude(post_type=user_profile.user_type).filter(description__icontains=keyword)
    posts = posts_description | posts_title
    context['posts'] = posts.distinct()
    context['form'] = form
    if len(context['posts']) == 0:
        messages.append("No results found")
    return render(request, 'cmumc/stream.html', context)

@login_required
def filter_available(request):
    context = {}
    messages = []
    context['messages'] = messages
    user_profile = get_object_or_404(Profile, user=request.user)
    posts = Post.objects.filter(deleted=False).exclude(post_type=user_profile.user_type).exclude(status='C').exclude(status='I')
    context['posts'] = posts
    if len(posts) == 0:
        messages.append("No Results Found.")
    return render(request, 'cmumc/stream.html', context)

# Ajax filter post
@login_required
def filter_post(request):
    user_profile = get_object_or_404(Profile, user=request.user)
    # Validation
    if request.method == 'GET':
        return redirect('stream')
    # Filter based on filtered items
    filtered_post = Post.objects.all()
    if 'date' in request.POST and request.POST['date']:
        date = request.POST['date']
        if date == 'today':
            filtered_post = filtered_post.filter(deleted=False).filter(date=timezone.now())
        if date == 'threedays':
            filtered_post = filtered_post.filter(deleted=False).filter(date__gte=timezone.now()).filter(date__lte=(timezone.now()+timedelta(days=3)))
        if date == 'aweek':
            filtered_post = filtered_post.filter(deleted=False).filter(date__gte=timezone.now()).filter(date__lte=(timezone.now()+timedelta(days=7)))

    if 'price[]' in request.POST and request.POST.getlist('price[]'):
        price_start = request.POST.getlist('price[]')[0]
        price_end = request.POST.getlist('price[]')[1]
        filtered_post = filtered_post.filter(deleted=False).filter(price__gte=price_start).filter(price__lte=(price_end))

    if 'tasktype[]' in request.POST and request.POST.getlist('tasktype[]'):
        tasktypes = request.POST.getlist('tasktype[]')
        result = Post.objects.none()
        for i in range(0, len(tasktypes)):
            taskType = tasktypes[i]
            temp = filtered_post.filter(category__exact=taskType)
            result = result | temp
        filtered_post = result

    if 'time[]' in request.POST and request.POST.getlist('time[]'):
        hour_start = int(request.POST.getlist('time[]')[0])
        min_start = int(request.POST.getlist('time[]')[1])
        hour_end = int(request.POST.getlist('time[]')[2])
        min_end = int(request.POST.getlist('time[]')[3])
        time_start = datetime.time(hour_start, min_start)
        time_end = datetime.time(hour_end, min_end)
        filtered_post = filtered_post.filter(deleted=False).filter(time__gte=time_start).filter(time__lte=(time_end))

    else:
        return redirect('stream')
    filtered_post = filtered_post.exclude(post_type=user_profile.user_type)
    response = Post.get_post_list_data(filtered_post)
    context = {}
    context['data'] = response
    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type="application/json")


@login_required
def clear_filter(request):
    return redirect('stream')

@login_required
def rate_task(request, post_id):
    context = {}
    messages = []
    context['messages'] = messages
    post_item = get_object_or_404(Post, post_id=post_id)
    task_item = get_object_or_404(Task, post=post_item)

    new_rating = Rating(created_user=request.user, task=task_item)
    form = RateForm(request.POST, instance=new_rating)
    context['form'] = form

    if not form.is_valid():
        messages.append("Form contained invalid data")
        return render(request, 'cmumc/rating.html', context)

    form.save()

    ##update rated user score
    rated_user_type = form.cleaned_data['rated_user_type']
    if rated_user_type == 'H':
        rated_user = task_item.helper
    else:
        rated_user = task_item.receiver

    rated_user_profile = get_object_or_404(Profile, user=rated_user)

    if rated_user_type == 'H':
        task_set = Task.objects.filter(helper=rated_user).filter(task_status='C')
    else:
        task_set = Task.object.filter(receiver=rated_user).filter(task_status='C')

    rating_set = Rating.objects.filter(task__in=task_set).filter(rated_user_type=rated_user_type)
    total_score = 0.0
    length = len(rating_set)
    for i in range(0, length):
        total_score += rating_set[i].score

    if rated_user_type == 'H':
        rated_user_profile.helper_score = total_score / length
    else:
        rated_user_profile.receiver_score = total_score / length

    return render(request, 'cmumc/mytask.html', context)










