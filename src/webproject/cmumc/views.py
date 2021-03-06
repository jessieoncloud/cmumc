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
import datetime
from datetime import timedelta
from django.utils import timezone
import json
from django.core.serializers.json import DjangoJSONEncoder
from decimal import *
import os

##twilio
from twilio import TwilioRestException
from twilio.rest import TwilioRestClient

account_sid = os.environ.get('ACCOUNT_SID', '{{ACCOUNT_SID}}')
auth_token  = os.environ.get('AUTH_TOKEN', '{{AUTH_TOKEN}}')
twilio_number = os.environ.get('TWILIO_NUMBER', '{{TWILIO_NUMBER}}')
client = TwilioRestClient(account_sid, auth_token)

def home(request):
    return render(request, 'cmumc/index.html', {})

@login_required
def stream(request):
    """
    View all helper posts if in receiver mode, or all receiver posts if in helper mode.
    """
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
    """
    View specific post information given the post's post_id.
    """
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
        if user_profile.user_type == post_item.post_type and request.user != post_item.created_user:
            return redirect('stream')
        if len(post_item.accept_list.filter(username=request.user.username)) != 0:
            context['accepted'] = True
        return render(request, 'cmumc/view_post.html', context)

@login_required
@transaction.atomic
def send_post(request):
    """
    Create a new post.
    """
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

@login_required
def mytask(request):
    """
    View all tasks related to the current user
    """
    context = {}
    user_item = get_object_or_404(User, username=request.user.username)
    user_profile = get_object_or_404(Profile, user=request.user)
    user_post = Post.objects.filter(created_user=request.user).filter(deleted=False).filter(post_type=user_profile.user_type)
    accept_post = user_item.post_set.filter(deleted=False).exclude(post_type=user_profile.user_type)
    context['user_post'] = user_post
    context['accept_post'] = accept_post
    return render(request,'cmumc/mytask.html', context)

def notification(post_id):
    """
    Notify helper and receiver when task is in progress or complete, return whether the message is sent successfully or not.
    """
    post_item = get_object_or_404(Post, post_id=post_id)
    if post_item.status == 'I':
        msg_body = "Your task \"" + post_item.title + "\" is now in progress."
    elif post_item.status == 'C':
        msg_body = "Your task \"" + post_item.title + "\" is now complete! Please rate this task on CMUMC."

    task_item = get_object_or_404(Task, post=post_item)
    recipient_list = [task_item.helper, task_item.receiver]
    for recipient in recipient_list:
        to_profile = Profile.objects.get(user=recipient)
        try:
            message = client.messages.create(body=msg_body,
                                             to=str(to_profile.phone),
                                            from_=twilio_number)
            success = True
        except TwilioRestException as e:
            print(e)
            success = False

    return success


@login_required
@transaction.atomic
def edit_post(request, post_id):
    """
    Edit a post given post's post_id.
    """
    context = {}
    errors = []
    context['errors'] = errors
    post_item = get_object_or_404(Post, post_id=post_id)
    if post_item.status == 'I' or post_item.status == 'C':
        return redirect('viewPost', post_id = post_id)
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
            return render(request, 'cmumc/edit_post.html', context)
    else:
        post_form = PostForm(instance=post_item)
    return render(request, 'cmumc/edit_post.html', {'form': post_form, 'post':post_item})

@login_required
@transaction.atomic
def delete_post(request, post_id):
    """
    Delete a post given post's post_id.
    """
    post_item = get_object_or_404(Post, post_id=post_id)
    if post_item.status == 'I' or post_item.status == 'C':
        return redirect('viewPost', post_id = post_id)
    if post_item.created_user != request.user:
        return redirect('stream')
    post_item.deleted = True
    post_item.save()
    return redirect('mytask')

@login_required
@transaction.atomic
def accept_post(request, post_id):
    """
    Accept the post.
    """
    context = {}
    errors = []
    context['errors'] = errors
    post_item = get_object_or_404(Post, post_id=post_id)

    if post_item.status == 'I' or post_item.status == 'C':
        errors.append("You cannot accept for this post")
        return render(request, 'cmumc/error.html', context)
    else:
        post_item.accept_list.add(request.user)
        post_item.status = 'NC'
        post_item.save()

        return redirect('mytask')

@login_required
def view_accept_list(request, post_id):
    """
    View the accepted user list for a post given the post's post_id.
    """
    context = {}
    post_item = get_object_or_404(Post, post_id=post_id)
    accept_list = post_item.accept_list.all()
    context['accept_list'] = accept_list
    user_item = get_object_or_404(User, username=request.user.username)
    user_profile = get_object_or_404(Profile, user=request.user)
    user_post = Post.objects.filter(created_user=request.user).filter(deleted=False).filter(
        post_type=user_profile.user_type)
    accept_post = user_item.post_set.filter(deleted=False).exclude(post_type=user_profile.user_type)
    context['user_post'] = user_post
    context['accept_post'] = accept_post

    return render(request, 'cmumc/mytask.html', context)

@login_required
@transaction.atomic
def accept(request, post_id):
    """
    Choose one user from accept_list to accept.
    """
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
    return redirect('mytask')
    

@login_required
@transaction.atomic
def complete(request, post_id):
    """
    Complete a task. Task status will be marked as "C"
    """
    context = {}
    errors = []
    context['errors'] = errors
    message = []
    context['message'] = message
    post_item = get_object_or_404(Post, post_id=post_id)

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
        return redirect('mytask')
    else:
        return redirect('mytask')

@login_required
def mode(request):
    """
    Choose to log in helper or receiver mode.
    """
    context = {}
    if request.method == 'GET':
        context['helper_form'] = ModeForm()
        context['receiver_form'] = ModeForm()
        return render(request, 'cmumc/mode.html', context)

    form = ModeForm(request.POST)
    print(form)
    user_profile = get_object_or_404(Profile, user=request.user)
    modename = form.cleaned_data.get('mode')
    user_profile.user_type = modename
    user_profile.save()
    return redirect('stream')

@login_required
def switch(request):
    """
    Switch current mode.
    """
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
    """
    View a user's profile.
    """
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
    helper_rating_list = Rating.objects.filter(task__in=helper_task).filter(rated_user_type='H')
    context['helper_rating_list'] = helper_rating_list
    receiver_task = Task.objects.filter(receiver=user_item)
    receiver_rating_list = Rating.objects.filter(task__in=receiver_task).filter(rated_user_type='R')
    context['receiver_rating_list'] = receiver_rating_list
    return render(request, 'cmumc/profile.html', context)

@login_required
def get_photo(request, user_name):
    """
    Get a user's photo.
    """
    user_item = get_object_or_404(User, username=user_name)
    profile = get_object_or_404(Profile, user=user_item)
    if not profile.photo:
        raise Http404

    content_type = guess_type(profile.photo.name)
    return HttpResponse(profile.photo, content_type=content_type)

@login_required
def get_post_photo(request, post_id):
    """
    Get a post's photo. If not uploaded, use the default photo for this category.
    """
    post_item = get_object_or_404(Post, post_id=post_id)
    if not post_item.post_photo:
        print("here")
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
    """
    Update a user's profile.
    """
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
            user_form.save()
            profile_form.save()
            return redirect('profile', user_name=request.user.username)
        else:
            return render(request, 'cmumc/edit_profile.html', context)
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=user_profile)
    return render(request, 'cmumc/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@transaction.atomic
def register(request):
    """
    User registration.
    """
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

    user_profile = Profile(user=new_user, activation_key=token)
    user_profile.save()

    email_body = """
Welcome to cmumc! Please click the link below to verify your email address and complete the registration of your account:
https://%s%s
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
    """
    Confirm registration.
    """
    try:
        user_item = User.objects.get(username=user_name)
        user_profile = Profile.objects.get(user=user_item)
        if user_profile.activation_key == token:
            user_item.is_active = True
            user_item.save()
            login(request, user_item)
        return redirect('mode')
    except:
        context = {}
        errors = []
        context['errors'] = errors
        errors.append("Registration failed")
        return render(request, 'cmumc/error.html', context)

@login_required
def send_message(request, post_id):
    """
    Send message to the post's created_user.
    """
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

    sent = messaging(to_profile, msg_body)

    if sent:
        msgs.append("Your message has been sent sucessfully")
    else:
        msgs.append("Sent failed. The person you want to sent SMS to has not set up his/her phone number.")

    return render(request, 'cmumc/contact.html', context)

@login_required
def search_post(request):
    """
    Search posts if the title or description contain the keyword, case insensitive.
    """
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
    all_post = posts.distinct()
    context['data'] = Post.get_post_list_data(all_post)
    if len(context['data']) == 0:
        messages.append("No results found")
    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type="application/json")

@login_required
def filter_available(request):
    """
    Show available posts based on current page results using Ajax.
    """
    context = {}
    messages = []
    context['messages'] = messages
    user_profile = get_object_or_404(Profile, user=request.user)
    filtered_post = Post.objects.none()
    if 'posts[]' in request.POST and request.POST.getlist('posts[]'):
        post_list = request.POST.getlist('posts[]')
        for i in range(0, len(post_list)):
            post_id = post_list[i]
            try:
                cur_post = Post.objects.filter(post_id=post_id)
            except:
                cur_post = Post.objects.none()
            filtered_post = filtered_post | cur_post

    posts = filtered_post.filter(deleted=False).exclude(post_type=user_profile.user_type).exclude(status='C').exclude(status='I')
    if len(posts) == 0:
        messages.append("No Results Found.")

    response = Post.get_post_list_data(posts)
    context['data'] = response
    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type="application/json")

@login_required
def filter_post(request):
    """
    Filter posts using Ajax.
    """
    user_profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'GET':
        return redirect('stream')

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
    """
    Clear filter criteria and redirect to stream.
    """
    return redirect('stream')

@login_required
def rate_task(request, post_id):
    """
    Rate the task and update related user's score.
    """
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
        return redirect('mytask')

    ##check if the rating already exists
    rating_item = Rating.objects.filter(created_user=request.user).filter(task=task_item)
    if len(rating_item) != 0:
        messages.append("This task has already been rated")
        return redirect('mytask')

    form.save()

    ##update rated user score
    rated_user_type = form.cleaned_data['rated_user_type']
    if rated_user_type == 'H':
        rated_user = task_item.helper
        task_item.receiver_status = 'R'
    else:
        rated_user = task_item.receiver
        task_item.helper_status = 'R'
    task_item.save()

    if task_item.helper_status == 'R' and task_item.receiver_status == 'R':
        task_item.status = 'R'
        task_item.save()

    rated_user_profile = get_object_or_404(Profile, user=rated_user)

    if rated_user_type == 'H':
        task_set = Task.objects.filter(helper=rated_user).exclude(task_status='I')
    else:
        task_set = Task.objects.filter(receiver=rated_user).exclude(task_status='I')

    rating_set = Rating.objects.filter(task__in=task_set).filter(rated_user_type=rated_user_type)
    total_score = Decimal(0.0)
    length = len(rating_set)
    for i in range(0, length):
        total_score = total_score + rating_set[i].score

    if rated_user_type == 'H':
        rated_user_profile.helper_score = total_score / length
    else:
        rated_user_profile.receiver_score = total_score / length
    rated_user_profile.save()

    rated_user_profile.save()
    return redirect('mytask')

@login_required
def contact(request, username):
    """
    Contact a specific user from the profile page.
    """
    user_item = get_object_or_404(User, username=username)
    to_profile = get_object_or_404(Profile, user=user_item)
    from_profile = get_object_or_404(Profile, user=request.user)

    context = {}
    msgs = []
    context['msgs'] = msgs
    context['form'] = MessageForm()

    if request.method == "GET":
        return render(request, 'cmumc/contact.html', context)

    form = MessageForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        msgs.append("Your message is not valid.")
        return render(request, 'cmumc/contact.html', context)
    body = form.cleaned_data['body']

    msg_body = "Message from CMUMC.\n\n"\
            + from_profile.user.username + " would like to send you a message:\n\n" + body + "\n \n" \
            + "You can contact him/her by " + str(from_profile.phone)

    sent = messaging(to_profile, msg_body)
    if sent:
        msgs.append("Your message has been sent successfully")
    else:
        msgs.append("Sent failed. The person you want to sent SMS to has not set up his/her phone number.")

    return render(request, 'cmumc/contact.html', context)

@login_required
def messaging(to_profile, msg_body):
    try:
        message = client.messages.create(body=msg_body,
                                         to=str(to_profile.phone),
                                         from_=twilio_number)
        return True
    except TwilioRestException as e:
        return False