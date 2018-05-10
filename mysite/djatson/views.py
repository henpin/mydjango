# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from .models import URLData

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
        context['object'] = get_object_or_404(URLData,name=name)

        return context

def get_chat_js(req, name):
    """ chat画面JS生成する"""
    # データ取得
    url_data = get_object_or_404(URLData, name=name)

    # JS生成
    with open(TEMPLATE_CHAT_JS_PATH) as f :
        # テンプレ読み込む
        js_template = f.read()

    # JS形式に置き換え
    ws_id = '"%s"' % (url_data.ws_id,)
    initialized = 'true' if url_data.state == u'active' else 'false'

    # テンプレートに情報注入
    js_template = js_template.replace(str("{{ WS_ID }}"), str(ws_id))
    js_template = js_template.replace(str("{{ INITIALIZED }}"), str(initialized)) # フォーム名

    return HttpResponse(js_template, content_type="text/javascript; charset=UTF-8")

def do_initialize(req,name):
    """ watsonを初期化する """
    # データ取得
    url_data = get_object_or_404(URLData, name=name)
    state = url_data.state

    # 初期化中でなければ許可
    if state != "initializing":
        # 初期化
        tasks.initialize_watson.delay(url_data)

    # adminにリダイレクト
    return HttpResponseRedirect('/admin/djatson/urldata/')


# ワトソンインターフェイス
WATSON = WatsonInterface()


def call_conversation(req):
    """ カンバゼーション呼び出す """
    # POSTだけ処理
    if req.method == 'POST':
        # データ取得
        ws_id = req.POST["ws_id"]
        _input = req.POST["input"]
        url_data = get_object_or_404(URLData, ws_id=ws_id)

        # 状態チェック
        if url_data.state != "active":
            return HttpResponse("fail")

        # ワトソンインターフェイスで会話
        res = WATSON.talk(_input,ws_id,"natural",max_=5)

        # jsonにして返す
        _json = json.dumps({ "response" : res.decode("utf-8") },ensure_ascii=False)

        return HttpResponse(_json,content_type="application/javascript; charset=UTF-8")


class JsonView(generic.TemplateView):
    """ デモHTMLを描画 """
    template_name = "djatson/view_json.html"

    def get_context_data(self, **kwargs):
        # コンテキスト取得
        context = super(JsonView, self).get_context_data(**kwargs)
        # データ取得
        name = kwargs["name"]
        context['object'] = get_object_or_404(URLData,name=name)

        return context

def get_view_json_js(req, name):
    """ jsonビュアーJSの生成 """
    # データ取得
    url_data = get_object_or_404(URLData, name=name)
    json_data = url_data.json.replace(u"\\",u"\\\\").replace(u"'",u"\\'")

    # JS生成
    with open(TEMPLATE_JSON_JS_PATH) as f :
        # テンプレ読み込む
        js_template = f.read()

    # テンプレートに情報注入
    js_template = js_template.replace(str("{{ JSON }}"), str(json_data))

    return HttpResponse(js_template, content_type="text/javascript; charset=UTF-8")




