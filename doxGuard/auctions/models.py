from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name="user_image")
    image = models.ImageField(upload_to='images/')


class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name="user_video")
    video = models.FileField(upload_to='video/')
