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

# Create your views here.
def home(request):
    return render(request, 'cmumc/index.html', {})

@login_required
def stream(request):
    context = {}
    user_profile = get_object_or_404(Profile, user=request.user)
    if user_profile.user_type == 'H':
        all_posts = Post.objects.filter(post_type='R').filter(deleted=False)
    else:
        all_posts = Post.objects.filter(post_type='H').filter(deleted=False)
    context['post'] = all_posts
    context['profile'] = user_profile
    return render(request, 'cmumc/stream.html', context)

@login_required
def view_post(request, post_id):
    context = {}
    errors = []
    context['errors'] = errors
    post_item = get_object_or_404(Post, post_id=post_id)
    if post_item.deleted:
        errors.append("The post has been deleted")
        return render(request, 'cmumc/error.html', context)
    else:
        context['post'] = post_item
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
        form = PostForm(request.POST, instance=new_post)
        context['form'] = form
        context['profile'] = user_profile

        if not form.is_valid():
            print("hee")
            print(form.errors)
            return redirect('stream')

        form.save()
        print("there")
        return redirect('stream')
    else:
        return render(request, 'cmumc/login.html', context)

# to be implemented 
# return all tasks related to the current user
@login_required
def mytask(request):
    return render(request,'cmumc/mytask.html',{})

@login_required
@transaction.atomic
def edit_post(request, post_id):
    context = {}
    post_item = get_object_or_404(Post, post_id=post_id)
    if request.method == 'POST':
        post_form = PostForm(request.POST, instance=post_item)
        context['form'] = post_form
        if post_form.is_valid():
            post_form.save()
            return redirect('viewPost', post_id = post_id)
        else:
            return render(request, 'cmumc/edit_post.html', context)
    else:
        post_form = PostForm(instance=post_item)
    return render(request, 'cmumc/edit_post.html', {'form': post_form})

@login_required
@transaction.atomic
def delete_post(request, post_id):
    context = {}
    post_item = get_object_or_404(Post, post_id=post_id)
    post_item.deleted = True
    return render(request, 'cmumc/stream.html', context)

@login_required
@transaction.atomic
def accept_post(request, post_id):
    context = {}
    errors = []
    context['errors'] = errors
    user_item = get_object_or_404(User, username=request.user.username)
    user_profile = get_object_or_404(Profile, user=request.user)
    post_item = get_object_or_404(Post, post_id=post_id)
    user_post = Post.get_user_posts
    context['user_post'] = user_post
    accept_post = user_item.post_set.exclude(post_type=user_profile.user_type)
    context['accept_post'] = accept_post

    if post_item.status == 'I' or post_item.status == 'C':
        errors.append("You cannot accept for this post")
        return render(request, 'cmumc/error.html', context)
    else:
        post_item.accept_list.add(request.user)
        post_item.status = 'NC'
        post_item.save()
        return render(request, 'cmumc/mytask.html', context)

##using ajax
@login_required
def view_accept_list(request, post_id):
    context = {}
    post_item = get_object_or_404(Post, post_id=post_id)
    accept_list = post_item.accept_list.all()
    context['accept_list'] = accept_list

    user_item = get_object_or_404(User, username=request.user.username)
    user_profile = get_object_or_404(Profile, user=request.user)
    user_post = Post.get_user_posts
    context['user_post'] = user_post
    accept_post = user_item.post_set.exclude(post_type=user_profile.user_type)
    context['accept_post'] = accept_post

    return render(request, 'cmumc/mytask.html', context)

##choose one user from accept_list to accept
@login_required
@transaction.atomic
def accept(request, post_id, username):
    context = {}
    errors = []
    context['errors'] = errors

    user_item = get_object_or_404(User, username=request.user.username)
    user_profile = get_object_or_404(Profile, user=request.user)
    post_item = get_object_or_404(Post, post_id=post_id)
    user_post = Post.get_user_posts
    context['user_post'] = user_post
    accept_post = user_item.post_set.exclude(post_type=user_profile.user_type)
    context['accept_post'] = accept_post

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
    return render(request, 'cmumc/mytask.html', context)

@login_required
@transaction.atomic
def complete(request, post_id):
    context = {}
    errors = []
    context['errors'] = errors

    user_item = get_object_or_404(User, username=request.user.username)
    user_profile = get_object_or_404(Profile, user=request.user)
    post_item = get_object_or_404(Post, post_id=post_id)
    user_post = Post.get_user_posts
    context['user_post'] = user_post
    accept_post = user_item.post_set.exclude(post_type=user_profile.user_type)
    context['accept_post'] = accept_post

    if not post_item.status == 'I':
        errors.append("This post status is not in progress and you cannot complete it")
        return render(request, 'cmumc/error.html', context)

    try:
        task_item = Task.objects.get(post=post_item)
    except:
        task_item = Task(post=post_item)
    if user_profile.user_type == 'H':
        task_item.helper_status = 'C'
    else:
        task_item.receiver_status = 'C'
    task_item.save()
    if task_item.helper_status == 'C' and task_item.receiver_status == 'C':
        task_item.task_status = 'C'
        task_item.save()
        post_item.status = 'C'
        post_item.save()
        return render(request, 'cmumc/mytask.html', context)
    else:
        return render(request, 'cmumc/mytask.html', context)

@login_required
def mode(request):
    context = {}
    if request.method == 'GET':
        context['form'] = ModeForm()
        return render(request, 'cmumc/mode.html', context)

    form = ModeForm(request.POST)

    user_profile = get_object_or_404(Profile, user=request.user)
    modename = form.cleaned_data['modename']
    user_profile.user_type = modename
    return redirect('stream')

@login_required
def switch(request):
    user_item = get_object_or_404(User, username=request.user.username)
    try:
        user_profile = Profile.objects.get(user=user_item)
    except:
        user_profile = Profle(user=user_item)
    if user_profile.user_type == 'H':
        user_profile.user_type = 'R'
    else:
        user_profile.user_type = 'H'
    user_profile.save()
    return render(request, 'cmumc/stream.html', {})

@login_required
def profile(request, user_name):
    context = {}
    user_item = get_object_or_404(User, username=user_name)
    try:
        user_profile = Profile.objects.get(user=user_item)
    except:
        user_profile = Profile(user=user_item)
    context['profile'] = user_profile
    user_post = Post.get_user_posts(user_item)
    context['post'] = user_post
    return render(request, 'cmumc/profile.html', context)

def get_photo(request, user_name):
    user_item = get_object_or_404(User, username=user_name)
    profile = get_object_or_404(Profile, user=user_item)
    if not profile.photo:
        raise Http404

    content_type = guess_type(profile.photo.name)
    return HttpResponse(profile.photo, content_type=content_type)

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
            # Logs in the new user and redirects to his/her profile page
            new_user = authenticate(username=user_item.username, \
                            password=user_item.password)
            login(request, new_user)
        return redirect('index')
    except:
        return redirect('index')



