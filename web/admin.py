from django.contrib import admin

from . import models
admin.site.register(models.Event)
admin.site.register(models.Assignment)
admin.site.register(models.NewUser)
admin.site.register(models.UserProgress)
