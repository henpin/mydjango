# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name="index"),
    url(r"^(?P<pk>[0-9]+)/$", views.DetailView.as_view(), name="detail"),
    url(r"^(?P<pk>[0-9]+)/results/$", views.ResultView.as_view(), name="results"),
    url(r"^(?P<q_id>[0-9]+)/vote/$", views.vote, name="vote"),
    url(r"^kaminaga/(?P<form_name>[a-zA-Z0-9]+)\.js/$", views.get_js, name="get_js")
]


