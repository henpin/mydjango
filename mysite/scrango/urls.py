# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from . import views

# restframework Router
router = DefaultRouter()
router.register(r'scrape',views.ScrapeAPIVS,base_name="scrape") # APIでクローラーVSにルーティング
router.register(r'notification_test',views.NotificationTestAPIVS,base_name="notification_test") # APIでクローラーVSにルーティング

urlpatterns = [
    url(r'^api/', include(router.urls)), # restframework rooter
    url(r"^scrape/(?P<_uuid>[a-zA-Z0-9_\-]+)/$", views.do_scrape, name="do_scrape"), # スクレイピングする
    url(r"^view_result/(?P<_uuid>[a-zA-Z0-9_\-]+)/$", views.ViewResultView.as_view(), name="view_result_view"), # 結果確認画面
    url(r"^view_result/(?P<_uuid>[a-zA-Z0-9_\-]+)\.js/$", views.get_view_result_js, name="get_view_result_js"), # 結果確認JS
]
