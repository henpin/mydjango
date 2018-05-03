# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from .models import URLData

# JS template file
TEMPLATE_JS_PATH = os.path.dirname(os.path.abspath(__file__)) + '/static/chat.js'

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
    with open(TEMPLATE_JS_PATH) as f :
        # テンプレ読み込む
        js_template = f.read()

    # JS形式に置き換え
    ws_id = '"%s"' % (url_data.ws_id,)
    initialized = 'true' if url_data.initialized else 'false'

    # テンプレートに情報注入
    js_template = js_template.replace(str("{{ WS_ID }}"), str(ws_id))
    js_template = js_template.replace(str("{{ INITIALIZED }}"), str(initialized)) # フォーム名

    return HttpResponse(js_template, content_type="text/javascript; charset=UTF-8")
