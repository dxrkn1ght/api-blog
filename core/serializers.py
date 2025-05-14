from rest_framework import serializers
from users.models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'avatar', 'followers_count', 'following_count']

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def validate_bio(self, value):
        if len(value) > 300:
            raise serializers.ValidationError("Bio 300 ta belgidan oshmasligi kerak.")
        return value

    def validate_avatar(self, value):
        max_size = 2 * 1024 * 1024  # 2MB
        if value and value.size > max_size:
            raise serializers.ValidationError("Avatar hajmi 2MB dan oshmasligi kerak.")
        return value

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and instance.user != request.user:
            raise serializers.ValidationError("Siz faqat o'z profilingizni o'zgartirishingiz mumkin.")
        return super().update(instance, validated_data)
