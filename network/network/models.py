from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField('self', symmetrical=False, blank=True)

    def count_followers(self):
        return self.followers.count()
    
    def count_following(self):
        return User.objects.filter(followers=self).count()

class Post(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)
    likers = models.ManyToManyField(User, related_name="posts_liked", blank=True)