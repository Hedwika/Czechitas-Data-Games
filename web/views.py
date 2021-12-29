import os
from urllib import request

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth.decorators import login_required

from czechitas_data_games import settings

from web import models
from web.forms import RightAnswer
from web.models import NewUser, Assignment, Event

import datetime


class TitlePageView(ListView):
  model = models.Event
  template_name = "web/title_page.html"

  def get_queryset(self):
      query_set = models.Event.objects.filter(end__gt=datetime.datetime.now())
      return query_set

class WikiView(ListView):
    model = models.Event
    template_name = "web/wiki.html"

    def get_queryset(self):
        query_set = models.Event.objects.filter(end__lt=datetime.datetime.now())
        return query_set

class AssignmentView(FormView):
    form_class = RightAnswer
    template_name = "assignment.html"

    def get_assignment(self, queryset=None):
        user: NewUser = NewUser.objects.filter(user=self.request.user).first()
        assignment = user.get_assignment(self.kwargs['event'])
        return assignment

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        kwargs = self.get_form_kwargs()
        kwargs["assignment"] = self.get_assignment()
        return form_class(**kwargs)

    def get(self, request, *args, **kwargs):
        if not self.get_assignment():
            return HttpResponseRedirect(f"/gratulujeme/")
        return super(AssignmentView, self).get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = RightAnswer(request.POST or None, assignment=self.get_assignment())
        if form.is_valid():
            user: NewUser = NewUser.objects.filter(user=self.request.user).first()
            user.solve_assignment(self.kwargs['event'], self.get_assignment())
            if not self.get_assignment():
                return HttpResponseRedirect(f"/gratulujeme/")
            else:
                return HttpResponseRedirect(f"/ukoly/{self.kwargs['event']}")
        return render(request, self.template_name, {"form": form, "assignment": self.get_assignment()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assignment"] = self.get_assignment()
        return context

    def download(request,path):
        file_path=os.path.join(settings.MEDIA_ROOT,path)
        if os.path.exists(file_path):
            with open(file_path, 'rb')as fh:
                response = HttpResponse(fh.read(),content_type="application/data")
                response['Content-Disposition'] = 'inline;filename='+os.path.basename(file_path)
                return response

        raise Http404

class CongratsView(ListView):
    template_name = 'congrats.html'

    def get_queryset(self):
        query_set = models.Event.objects.filter()
        return query_set

    def congrats(request):
        return render(request, "congrats.html")