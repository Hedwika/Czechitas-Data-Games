"""czechitas_data_games URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include

from czechitas_data_games import settings
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from django.views.static import serve
from web import views

from web.accounts.views import login_view, logout_view, register_view
from django_email_verification import urls as mail_urls
from django.urls import path
from web import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('prihlaseni/', login_view, name='prihlaseni'),
    path('odhlaseni/', login_required(logout_view), name='odhlaseni'),
    path('registrace/', register_view, name='registrace'),
    path('ukoly/<int:event>', login_required(views.AssignmentView.as_view()), name='ukoly'),
    path('gratulujeme/', login_required(views.CongratsView.as_view()), name='gratulujeme'),
    url(r'^download/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),
    path('email/', include(mail_urls)),
    path('', views.TitlePageView.as_view(), name='title_page'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
