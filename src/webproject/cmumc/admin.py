from django.contrib import admin
from django.forms.widgets import TextInput

from django_google_maps.widgets import GoogleMapsAddressWidget
from django_google_maps.fields import AddressField, GeoLocationField

from .models import *

# Register your models here.
class PostAdmin(admin.ModelAdmin):
	readonly_fields = ('created_time',)
	formfield_overrides = {
		AddressField: {'widget': GoogleMapsAddressWidget},
		GeoLocationField: {'widget': TextInput(attrs={'readonly': 'readonly'})},
	}

admin.site.register(Post, PostAdmin)
admin.site.register(Profile)