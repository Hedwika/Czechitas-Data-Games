from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.core.mail import EmailMessage
from django.contrib import messages
from django_email_verification import send_email
from django.views.decorators.csrf import csrf_exempt

from .forms import LoginForm, RegisterForm

@csrf_exempt
def register_view(request, password=None):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")
        password1 = form.cleaned_data.get("password1")
        password2 = form.cleaned_data.get("password2")

        # try:
        # user = Users.objects.create_user(username=username, email=email, password=password1)
        user = get_user_model().objects.create_user(username=username, email=email, password=password1)
        user.is_active = False
        send_email(user)
        # return render(request, 'confirm_template.html')
        # except:
        #     user = None

        if user != None:
            return redirect("/prihlaseni")
        else:
            request.session['register_error'] = 1 # 1 == True

    return render(request, "forms.html", {"form": form})

def login_view(request):
    form = LoginForm(request.POST or None)
    error = ""
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        # print(password)
        user = authenticate(request, username=username, password=password)
        print(user)
        if user != None:
            # user is valid and active -> is_active
            # request.user == user
            login(request, user)
            return redirect("/")
        else:
            # attempt = request.session.get("attempt") or 0
            # request.session['attempt'] = attempt + 1
            # return redirect("/invalid-password")
            request.session['invalid_user'] = 1 # 1 == True
            error = "Nepoznali jsme vás: Vaše údaje nejsou správné, nebo váš účet není ověřen. Klikněte prosím na odkaz v e-mailu, pokud vám nepřišel, zkontrolujte Spambox."
    return render(request, "forms.html", {"form": form, "error": error})

def logout_view(request):
    logout(request)
    return render(request, "logout.html")