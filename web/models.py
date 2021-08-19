from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms

from web.accounts import forms

User = get_user_model()

class Event(models.Model):
    title = models.CharField(max_length=50, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    description = models.CharField(max_length=1000)

class Assignment(models.Model):
    description = models.CharField(max_length=1000)
    data = models.FileField(upload_to='media')
    right_answer = models.CharField(max_length=200)
    order = models.IntegerField()
    event = models.ForeignKey(Event, blank=True, null=True, on_delete=models.CASCADE)

class NewUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    todo_assignment = models.IntegerField(default=1)

    def __str__(self):
        return str(self.user.username)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        NewUser.objects.create(user=instance)