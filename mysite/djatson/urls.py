# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^kaminaga/chat/(?P<name>[a-zA-Z0-9_]+)/$", views.ChatView.as_view(), name="chat_view"), # チャット画面クエリ
    url(r"^kaminaga/chat/(?P<name>[a-zA-Z0-9_]+)\.js/$", views.get_chat_js, name="get_chat_js"), # チャットJSくえり
    url(r"^kaminaga/view_json/(?P<name>[a-zA-Z0-9_]+)$", views.JsonView.as_view(), name="json_view"), # jsonビューJSクエリ
    url(r"^kaminaga/view_json/(?P<name>[a-zA-Z0-9_]+)\.js/$", views.get_view_json_js, name="get_view_json_js"), # jsonビューJSクエリ
    url(r"^kaminaga/initialize/(?P<name>[a-zA-Z0-9_]+)/$", views.do_initialize, name="do_initialize"), # チャットJSくえり
    url(r"^kaminaga/conversation/$", views.call_conversation, name="call_conversation"), # チャットAjaxエンドポイント
]
