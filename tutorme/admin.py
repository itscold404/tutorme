from django.contrib import admin
from .models import Person, Post, Session_Request, Notification

# Register your models here.


class PersonAdmin(admin.ModelAdmin):
    list_display = ('email', 'last_name', 'first_name', 'person_type')
    ordering = ['email']
    
class PostAdmin(admin.ModelAdmin):
    
    list_display = ('creatorEmail', 'classes', 'hash', 'display_post','sessionRangeStart','sessionRangeEnd')
    ordering = ['classes']

class SessionRequestAdmin(admin.ModelAdmin):
    list_display = ('creator_email', 'status')
    ordering = ['creator_email']

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('is_read', 'message', 'timestamp', 'recipientEmail')
    ordering = ['recipientEmail']
    
admin.site.register(Person, PersonAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Session_Request, SessionRequestAdmin)
admin.site.register(Notification, NotificationAdmin)
