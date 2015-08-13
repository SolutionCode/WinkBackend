from django.contrib import admin
from .models import Friend
# Register your models here.

class FriendAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'friend_id', 'date_added')
    search_fields = \
        ['user_id__username', 'friend_id__username',
         'user_id__first_name', 'friend_id__first_name',
         'user_id__last_name', 'friend_id__last_name',
         'user_id__email', 'friend_id__email']
admin.site.register(Friend, FriendAdmin)