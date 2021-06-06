from django.db import models

class Event(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    description = models.CharField(max_length=1000)

class Assignment(models.Model):
    description = models.CharField(max_length=1000)
    data = models.FileField()
    right_answer = models.CharField(max_length=200)
    order = models.IntegerField()