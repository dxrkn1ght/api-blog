from django.db import models
from users.models import Profile

class Follow(models.Model):
    user = models.ForeignKey(Profile, related_name='following_set', on_delete=models.CASCADE)
    followed_user = models.ForeignKey(Profile, related_name='followers_set', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.user.username} follows {self.followed_user.user.username}'
