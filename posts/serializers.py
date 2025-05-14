from rest_framework import serializers
from .models import Post, Comment, Like


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'author', 'author_username', 'text', 'created_at']
        read_only_fields = ['id', 'author', 'author_username', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    comments = CommentSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'author_username',
            'content',
            'created_at',
            'comments',
            'like_count',
            'is_liked',
        ]
        read_only_fields = [
            'id',
            'author',
            'author_username',
            'created_at',
            'comments',
            'like_count',
            'is_liked',
        ]

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if user.is_authenticated:
                return obj.likes.filter(user=user).exists()
        return False


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
