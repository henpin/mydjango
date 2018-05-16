# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^kaminaga/scrape/(?P<name>[a-zA-Z0-9_]+)/$", views.do_scrape, name="do_scrape"), # チャットJSくえり
    url(r"^kaminaga/view_result/(?P<name>[a-zA-Z0-9_]+)/$", views.ViewResultView.as_view(), name="view_result_view"), # チャットJSくえり
    url(r"^kaminaga/view_result/(?P<name>[a-zA-Z0-9_]+)\.js/$", views.get_view_result_js, name="get_view_result_js"), # チャットJSくえり
]
