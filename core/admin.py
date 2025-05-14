from django.contrib import admin
from .models import Follow

class FollowAdmin(admin.ModelAdmin):
    list_display = ['user', 'followed_user', 'created_at']
    search_fields = ['user__user__username', 'followed_user__user__username']
    list_filter = ['created_at']
    ordering = ['created_at']

admin.site.register(Follow, FollowAdmin)
