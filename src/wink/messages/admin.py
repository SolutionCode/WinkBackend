from django.contrib import admin

from messages.models import Message

class MessageAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'created_at')
    search_fields = \
        ['from_user__username', 'to_user__username',
         'from_user__first_name', 'to_user__first_name',
         'from_user__last_name', 'to_user__last_name',
         'from_user__email', 'to_user__email']

admin.site.register(Message, MessageAdmin)
