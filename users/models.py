from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField('users.CustomUser', on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followed_by', blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='followed_to', blank=True)

    def __str__(self):
        return f"{self.user.username} profili"

    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()
