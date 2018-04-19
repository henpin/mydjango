# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^kaminaga/(?P<form_name>[a-zA-Z0-9]+)\.js/$", views.get_js, name="get_js"),
    url(r"^kaminaga/(?P<form_name>[a-zA-Z0-9]+)\.html/$", views.ResultView.as_view(), name="result_view")
]
