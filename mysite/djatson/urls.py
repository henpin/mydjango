# -*- coding: utf-8 -*-
from django.conf.urls import url,include
from rest_framework.routers import DefaultRouter
from . import views

# restframework Router
router = DefaultRouter()
router.register(r'crawl',views.CrawlActionVS,base_name="crawl") # クローリングする
router.register(r'keyword_crawl',views.KeywordCrawlActionVS,base_name="keyword_crawl") # キーワードクローリングする
router.register(r'initialize_fromCrawledData',views.Initialize_fromCrawledDataActionVS,base_name="initialize_fromCrawledData") # キーワードクローリングする

api_router = DefaultRouter()
api_router.register(r'cross_search',views.CrossSearchAPIVS,base_name="cross_search") # クローリングする


urlpatterns = [
    url(r'', include(router.urls)), # restframework rooter
    url(r'^api/', include(api_router.urls)), # restframework rooter
    url(r"^chat/(?P<name>[a-zA-Z0-9_\-]+)/$", views.ChatView.as_view(), name="chat_view"), # チャット画面クエリ
    url(r"^chat/(?P<name>[a-zA-Z0-9_\-]+)\.js/$", views.get_chat_js, name="get_chat_js"), # チャットJSくえり
    url(r"^view_json/(?P<name>[a-zA-Z0-9_\-]+)$", views.JsonView.as_view(), name="json_view"), # jsonビューJSクエリ
    url(r"^view_json/(?P<name>[a-zA-Z0-9_\-]+)\.js/$", views.get_view_json_js, name="get_view_json_js"), # jsonビューJSクエリ
    url(r"^initialize/(?P<name>[a-zA-Z0-9_\-]+)/$", views.do_initialize, name="do_initialize"), # チャットJSくえり
    url(r"^conversation/$", views.call_conversation, name="call_conversation"), # チャットAjaxエンドポイント
    url(r"^view_json2/(?P<name>[a-zA-Z0-9_\-]+)$", views.JsonView2.as_view(), name="json_view2"), # jsonビューJSクエリ
    url(r"^view_json2/(?P<name>[a-zA-Z0-9_\-]+)\.js/$", views.get_view_json_js2, name="get_view_json_js2"), # jsonビューJSクエリ
]
