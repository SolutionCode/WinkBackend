from django.contrib import admin

from friends.models import Friend


class FriendAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend', 'date_added')
    search_fields = \
        ['user__username', 'friend__username',
         'user__first_name', 'friend__first_name',
         'user__last_name', 'friend__last_name',
         'user__email', 'friend__email']

admin.site.register(Friend, FriendAdmin)