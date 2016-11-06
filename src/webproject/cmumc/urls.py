from django.conf.urls import include, url

import django.contrib.auth.views
import cmumc.views

urlpatterns = [
    url(r'^$', cmumc.views.home, name='index'),
    url(r'^login$', django.contrib.auth.views.login, {'template_name':'cmumc/login.html'}, name='login'),
    url(r'^logout$', django.contrib.auth.views.logout_then_login, name='logout'),
    url(r'^register$', cmumc.views.register, name='register'),
    url(r'^confirm-registeration/(?P<user_name>\w+)/(?P<token>[\w.-]+)$', cmumc.views.confirm_register, name='confirm'),
    url(r'^password_reset$', django.contrib.auth.views.password_reset, name='reset'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        django.contrib.auth.views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^password_reset_done$', django.contrib.auth.views.password_reset_done, name='password_reset_done'),
    url(r'^password_reset_complete$', django.contrib.auth.views.password_reset_complete,
        name='password_reset_complete'),
    url(r'^password_change', django.contrib.auth.views.password_change, {'post_change_redirect': '/'},
        name='password_change'),
    url(r'^password_change_done', django.contrib.auth.views.password_change_done, name='password_change_done'),
    url(r'^switch$', cmumc.views.switch, name='switch'),
    url(r'^profile/(?P<user_name>\w+)$', cmumc.views.profile, name='profile'),
    url(r'^edit_profile$', cmumc.views.update_profile, name='edit_profile'),
    url(r'^profile$', cmumc.views.profile, name='profile'),
    url(r'^photo/(?P<user_name>\w+)$', cmumc.views.get_photo, name='photo'),
    url(r'^mode$', cmumc.views.mode, name='mode'),
    url(r'^stream$', cmumc.views.stream, name='stream'),
    url(r'^send_post$', cmumc.views.send_post, name='create'),
    url(r'^edit_post/(?P<post_id>\d+)$', cmumc.views.edit_post, name='editPost'),
    url(r'^delete_post/(?P<post_id>\d+)$', cmumc.views.delete_post, name='deletePost'),
    url(r'^view_post/(?P<post_id>\d+)$', cmumc.views.view_post, name='viewPost'),
    url(r'^accept_post/(?P<post_id>\d+)$', cmumc.views.accept_post, name='acceptPost'),
    url(r'^accept_list/(?P<post_id>\d+)$', cmumc.views.view_accept_list, name='acceptList'),
    url(r'^accept/(?P<post_id>\d+)$', cmumc.views.accept, name='accept'),
    url(r'^complete/(?P<post_id>\d+)$', cmumc.views.complete, name='complete'),
]