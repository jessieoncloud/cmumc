from django.contrib import admin

from .models import *

# Register your models here.
class PostAdmin(admin.ModelAdmin):
	readonly_fields = ('created_time',)

admin.site.register(Post, PostAdmin)
admin.site.register(Profile)
admin.site.register(Task)
admin.site.register(Notification)
admin.site.register(Rating)