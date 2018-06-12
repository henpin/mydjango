# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets

from .models import CrawlerData, DjatsonLogData, CrawlingLogData, HtmlData

from watson_api.watson_interface import WatsonInterface
import tasks

# JS template file
TEMPLATE_CHAT_JS_PATH = os.path.dirname(os.path.abspath(__file__)) + '/static/chat.js'
TEMPLATE_JSON_JS_PATH = os.path.dirname(os.path.abspath(__file__)) + '/static/view_json.js'

# Create your views here.
class ChatView(generic.TemplateView):
    """ デモHTMLを描画 """
    template_name = "djatson/chat.html"

    def get_context_data(self, **kwargs):
        # コンテキスト取得
        context = super(ChatView, self).get_context_data(**kwargs)
        # データ取得
        name = kwargs["name"]
        context['object'] = get_object_or_404(CrawlerData,name=name)

        return context

def get_chat_js(req, name):
    """ chat画面JS生成する"""
    # データ取得
    crawler_data = get_object_or_404(CrawlerData, name=name)

    # JS生成
    with open(TEMPLATE_CHAT_JS_PATH) as f :
        # テンプレ読み込む
        js_template = f.read()

    # JS形式に置き換え
    ws_id = '"%s"' % (crawler_data.ws_id,)
    initialized = 'true' if crawler_data.state == u'active' else 'false'

    # テンプレートに情報注入
    js_template = js_template.replace(str("{{ WS_ID }}"), str(ws_id))
    js_template = js_template.replace(str("{{ INITIALIZED }}"), str(initialized)) # フォーム名

    return HttpResponse(js_template, content_type="text/javascript; charset=UTF-8")

def do_initialize(req,name):
    """ watsonを初期化する """
    # データ取得
    crawler_data = get_object_or_404(CrawlerData, name=name)
    state = crawler_data.state

    # 初期化中でなければ許可
    if state != "crawling":
        # 初期化
        tasks.initialize_watson.delay(crawler_data)

    # adminにリダイレクト
    return HttpResponseRedirect('/admin/djatson/crawlerdata/')


# ワトソンインターフェイス
WATSON = WatsonInterface()


def call_conversation(req):
    """ カンバゼーション呼び出す """
    # POSTだけ処理
    if req.method == 'POST':
        # データ取得
        ws_id = req.POST["ws_id"]
        _input = req.POST["input"]
        crawler_data = get_object_or_404(CrawlerData, ws_id=ws_id)

        # 状態チェック
        if crawler_data.state != "active":
            return HttpResponse("fail")

        # ワトソンインターフェイスで会話
        res = WATSON.talk(_input,ws_id,"natural",max_=5)

        # jsonにして返す
        _json = json.dumps({ "response" : res.decode("utf-8") },ensure_ascii=False)

        return HttpResponse(_json,content_type="application/javascript; charset=UTF-8")


class BaseJsonView(generic.TemplateView):
    """ JSON眺めるクラス基底 """
    # 依存性
    template_name = ""

    def get_context_data(self, **kwargs):
        # コンテキスト取得
        context = super(JsonView, self).get_context_data(**kwargs)
        # データ取得
        name = kwargs["name"]
        context['object'] = get_object_or_404(CrawlerData,name=name)

        return context
    

class JsonView(BaseJsonView):
    """ デモHTMLを描画 """
    template_name = "djatson/view_json.html"

class JsonView2(generic.TemplateView):
    """ クロール結果JSONを描画 """
    template_name = "djatson/view_json2.html"


def get_view_json_js(req, name):
    """ jsonビュアーJSの生成 """
    # データ取得
    crawler_data = get_object_or_404(CrawlerData, name=name)
    json_data = DjatsonLogData.objects.filter(crawler=crawler_data).latest("datetime").json.replace(u"\\",u"\\\\").replace(u"'",u"\\'")

    # JS生成
    with open(TEMPLATE_JSON_JS_PATH) as f :
        # テンプレ読み込む
        js_template = f.read()

    # テンプレートに情報注入
    js_template = js_template.replace(str("{{ JSON }}"), str(json_data))

    return HttpResponse(js_template, content_type="text/javascript; charset=UTF-8")

def get_view_json_js2(req, name):
    """ jsonビュアーJSの生成 """
    # データ取得
    crawler_data = get_object_or_404(CrawlerData, name=name)
    log_data = CrawlingLogData.objects.filter(crawler=crawler_data).latest("datetime") # 最新のログ

    # JSON構築
    data_dict = dict()
    # ログから全HTMLデータ抜く
    for html_data in HtmlData.objects.filter(crawlinglog=log_data):
        data_dict[html_data.url] = html_data.html # 詰め替え
        
    # JSON生成
    json_data = json.dumps(data_dict).replace(u"\\",u"\\\\").replace(u"'",u"\\'")

    # JS生成
    with open(TEMPLATE_JSON_JS_PATH) as f :
        # テンプレ読み込む
        js_template = f.read()

    # テンプレートに情報注入
    js_template = js_template.replace(str("{{ JSON }}"), str(json_data))

    return HttpResponse(js_template, content_type="text/javascript; charset=UTF-8")


# API
class CrawlActionVS(viewsets.ViewSet):
    """ クローリングAPIJビューセット"""
    def retrieve(self, request, pk=None):
        """ Getメソッド処理"""
        # データ取得
        crawler_data = get_object_or_404(CrawlerData, name=pk)

        # 初期化中でなければ許可
        if crawler_data.state != "crawling":
            tasks.do_crawl.delay(crawler_data) # 非同期クローリング開始

        # adminにリダイレクト
        return HttpResponseRedirect('/admin/djatson/crawlerdata/')




