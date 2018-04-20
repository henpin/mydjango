# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^kaminaga/(?P<form_name>[a-zA-Z0-9]+)\.js/$", views.get_js, name="get_js"),
    url(r"^kaminaga/demo/(?P<form_name>[a-zA-Z0-9]+)/$", views.ResultView.as_view(), name="result_view"),
    url(r"^kaminaga/logging/$", views.log_it, name="log_it"),
    url(r"^kaminaga/replay/(?P<uuid>[a-zA-Z0-9]+)/$", views.ReplayView.as_view(), name="replay_it")
]
