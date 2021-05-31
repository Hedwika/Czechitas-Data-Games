from django.db import models

class Event(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    description = models.CharField(max_length=1000)