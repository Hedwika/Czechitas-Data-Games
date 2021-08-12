from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from . import models

class TitlePageView(ListView):
  model = models.Event
  template_name = "web/title_page.html"

# @login_required
# use the @login_required(whole uncommented line 4) when views are created so users can not enter the content unsigned