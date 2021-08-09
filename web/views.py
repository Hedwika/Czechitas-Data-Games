import os
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

from czechitas_data_games import settings
from web import models

from web.forms import RightAnswer
from web.models import NewUser, Assignment


# @login_required
class AssignmentView(DetailView):
    model = models.Assignment
    template_name = "assignment.html"

    def get_object(self, queryset=None):
        user = NewUser.objects.filter(user=self.request.user).first()
        return models.Assignment.objects.filter(id=user.todo_assignment).first()

    def post(self, request, *args, **kwargs):
        form = RightAnswer(request.POST or None, right_answer=self.get_object().right_answer)
        answer = self.get_object().right_answer
        if form.is_valid():
            user = NewUser.objects.filter(user=self.request.user).first()
            user.todo_assignment += 1
            user.save()
            if user.todo_assignment == 10:
                return HttpResponseRedirect("/congrats")
            else:
                return HttpResponseRedirect("/assignment")

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