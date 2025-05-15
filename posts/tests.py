from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Post, Like, Comment

User = get_user_model()

class PostAppTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345678')

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_create_post(self):
        url = reverse('post-list')
        data = {'content': 'Test post'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)

    def test_like_and_unlike_post(self):
        post = Post.objects.create(author=self.user, content='Test post')
        url = reverse('post-like', args=[post.id])  # /api/posts/posts/<id>/like/

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Like.objects.count(), 0)

    def test_create_comment(self):
        post = Post.objects.create(author=self.user, content='Test post')
        url = reverse('comment-list')  # /api/posts/comments/
        data = {'text': 'Test comment', 'post': post.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
