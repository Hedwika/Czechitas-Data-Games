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
    timestamp = models.DateTimeField(auto_now=True)

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
    answer_type = models.CharField(max_length=100, choices=ANSWER_CHOICES, null=True)
    order = models.IntegerField()
    event = models.ForeignKey(Event, blank=True, null=True, on_delete=models.CASCADE)

class NewUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    todo_assignment = models.IntegerField(default=1)

    def get_assignment(self, event_id):
        user_progress_query = UserProgress.objects.filter(Q(new_user=self) & Q(event_id=event_id)).order_by("timestamp")
        assignment_queryset = Assignment.objects.filter(event_id=event_id).order_by("order")
        if not user_progress_query.exists():
            return assignment_queryset.first()
        else:
            user_progress: UserProgress = user_progress_query.last()
            current_assignment_order = user_progress.assignment.order + 1
            assignment_queryset = assignment_queryset.filter(order=current_assignment_order)
            if assignment_queryset.count() > 0:
                return assignment_queryset.first()
            else:
                return None

    def solve_assignment(self, event_id: int, assignment: Assignment):
        user_progress = UserProgress(event_id=event_id, new_user=self, assignment=assignment)
        user_progress.save()

    def __str__(self):
        return str(self.user.username)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        NewUser.objects.create(user=instance)