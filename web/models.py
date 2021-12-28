from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms
from sqlparse.tokens import Assignment
from web.accounts import forms
import datetime

User = get_user_model()

class Event(models.Model):
    title = models.CharField(max_length=50, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    description = models.CharField(max_length=1000)

    @property
    def is_currently_running(self):
        if self.start <= datetime.datetime.now() and self.end >= datetime.datetime.now():
            return True
        else:
            return False

class UserProgress(models.Model):
    event = models.ForeignKey("Event", blank=True, null=True, on_delete=models.CASCADE)
    new_user = models.ForeignKey("NewUser", blank=True, null=True, on_delete=models.CASCADE)
    assignment = models.ForeignKey("Assignment", blank=True, null=True, on_delete=models.CASCADE)

    def increase_assignment_order(self):
        self.assignment_order += 1
        self.save()

class Assignment(models.Model):
    description = models.TextField(max_length=5000)
    # Data are not required because of programming tasks and automated tests
    data = models.FileField(upload_to='media', null=True, blank=True)
    right_answer = models.CharField(max_length=200)
    ANSWER_CHOICES = [
        ('SEZNAM', 'SEZNAM'),
        ('ČÍSLO', 'ČÍSLO'),
        ('TEXT', 'TEXT'),
    ]
    answer_type = models.CharField(max_length=10, choices=ANSWER_CHOICES, null=True)
    order = models.IntegerField()
    event = models.ForeignKey(Event, blank=True, null=True, on_delete=models.CASCADE)

class NewUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    todo_assignment = models.IntegerField(default=1)

    def get_assignment(self, event_id):
        user_progress_query = UserProgress.objects.filter(Q(new_user=self) & Q(event_id=event_id))
        if not user_progress_query.exists():
            user_progress: UserProgress = UserProgress(new_user=self, event_id=event_id)
            user_progress.save()
        else:
            user_progress: UserProgress = user_progress_query.last()
        assignment_order = user_progress.assignment_order
        assignment_queryset = Assignment.objects.filter(Q(event_id=event_id) & Q(order=assignment_order))
        if assignment_queryset.count() > 0:
            return assignment_queryset.last()
        else:
            return None

    def solve_assignment(self, event_id):
        user_progress_query = UserProgress.objects.filter(Q(new_user=self) & Q(event_id=event_id))
        if user_progress_query.count() > 0:
            user_progress: UserProgress = user_progress_query.last()
            user_progress.increase_assignment_order()

    def __str__(self):
        return str(self.user.username)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        NewUser.objects.create(user=instance)