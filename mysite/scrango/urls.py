# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^kaminaga/scrape/(?P<name>[a-zA-Z0-9_]+)/$", views.do_scrape, name="do_scrape"), # チャットJSくえり
]
