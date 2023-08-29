import datetime
from django.db import models
from django.contrib.auth.models import User
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class Comment(MPTTModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    email = models.EmailField()
    text = models.TextField()
    image = models.ImageField(upload_to='images')
    text_file = models.FileField(upload_to='text_files', null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Log(models.Model):
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    message = models.TextField()

    def __str__(self):
        return self.message
