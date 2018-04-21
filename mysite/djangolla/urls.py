# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^kaminaga/(?P<form_name>[a-zA-Z0-9]+)\.js/$", views.get_js, name="get_js"), # JSクエリ
    url(r"^kaminaga/demo/(?P<form_name>[a-zA-Z0-9]+)/$", views.ResultView.as_view(), name="result_view"), # デモ画面クエリ
    url(r"^kaminaga/logging/$", views.log_it, name="log_it"), # ログAJax送信先
    url(r"^kaminaga/replay/(?P<uuid>[a-zA-Z0-9-_]+)/$", views.ReplayView.as_view(), name="replay_it"), # リプレイ画面クエリ
    url(r"^kaminaga/replay_js/(?P<_uuid>[a-zA-Z0-9-_]+)\.js/$", views.get_replay_js, name="get_replay_js"), # リプレイJSJクエリ
]
