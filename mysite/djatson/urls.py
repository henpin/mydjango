# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^kaminaga/chat/(?P<name>[a-zA-Z0-9]+)/$", views.ChatView.as_view(), name="chat_view"), # チャット画面クエリ
    url(r"^kaminaga/chat_js/(?P<name>[a-zA-Z0-9]+)\.js/$", views.get_chat_js, name="get_chat_js"), # チャットJSくえり
]
