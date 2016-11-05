from django.conf.urls import include, url

import django.contrib.auth.views
import cmumc.views

urlpatterns = [
    url(r'^$', cmumc.views.home, name='home'),
    url(r'^login$', django.contrib.auth.views.login, {'template_name':'cmumc/login.html'}, name='login'),
    url(r'^logout$', django.contrib.auth.views.logout_then_login, name='logout'),
    url(r'^register$', cmumc.views.register, name='register'),
    url(r'^confirm-registeration/(?P<user_name>\w+)/(?P<token>[\w.-]+)$', cmumc.views.confirm_register, name='confirm'),
]