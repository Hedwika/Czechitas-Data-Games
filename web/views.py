import os
from urllib import request

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
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

class AssignmentView(DetailView):
    model = models.Assignment
    template_name = "assignment.html"

    def get_object(self, queryset=None):
        user = NewUser.objects.filter(user=self.request.user).first()
        return models.Assignment.objects.filter(id=user.todo_assignment).first()

    # def get(self, request, *args, **kwargs):
    #     event_assignments = Assignment.objects.filter(event__title='Czechitas Data Games I.')
    #     number_of_tasks = len(event_assignments)
    #     user = NewUser.objects.filter(user=self.request.user).first()
    #
    #     if user.todo_assignment > number_of_tasks:
    #         return HttpResponseRedirect("/gratulujeme")
    #     else:
    #         return super(AssignmentView, self).get()

    def post(self, request, *args, **kwargs):
        form = RightAnswer(request.POST or None, right_answer=self.get_object().right_answer)
        answer = self.get_object().right_answer
        if form.is_valid():
            user = NewUser.objects.filter(user=self.request.user).first()
            user.todo_assignment += 1
            user.save()
            event_assignments = Assignment.objects.filter(event__title='Data Games I.')
            number_of_tasks = len(event_assignments)
            if user.todo_assignment > number_of_tasks:
                return HttpResponseRedirect("/gratulujeme")
            else:
                return HttpResponseRedirect("/ukoly")

        return render(request, "forms.html", {"form": form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = RightAnswer(right_answer=self.get_object().right_answer)
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