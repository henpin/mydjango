# -*- coding: utf-8 -*-
"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles import views
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^admin/', admin.site.urls, name="admin"),
    #url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    #url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^djangolla/',include("djangolla.urls")),
    url(r'^djatson/',include("djatson.urls")),
    url(r'^scrango/',include("scrango.urls")),
    url(r'^$', RedirectView.as_view(url='static/index.html'), name="index"),
    url(r'^auth/', include('social_django.urls', namespace='social')),
    url(r'social_login',TemplateView.as_view(template_name='social_login.html')) # ソーシャルログインデモページ
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

