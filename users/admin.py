from django.contrib import admin
from .models import CustomUser, Profile

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'date_joined')
    ordering = ('-date_joined',)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'avatar', 'followers_count', 'following_count')
    search_fields = ('user__username', 'bio')
    list_filter = ('user__is_active',)

    def followers_count(self, obj):
        return obj.followers.count()

    def following_count(self, obj):
        return obj.following.count()

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
