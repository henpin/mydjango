# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from .models import CrawlerData, ScraperData, ResultData

import tasks

# JS template file
TEMPLATE_JSON_JS_PATH = os.path.dirname(os.path.abspath(__file__)) + '/static/view_result.js'

# Create your views here.
def do_scrape(req,name):
    """ スクレイピングする """
    # データ取得
    crawler_data = get_object_or_404(CrawlerData, name=name)

    # 状態変遷
    if crawler_data.url :
        # 状態変遷
        crawler_data.state = "executing" # 状態-> エラー
        crawler_data.save()
        # スクレイピング開始
        tasks.do_scrape.delay(crawler_data)
    else :
        # 状態変遷
        crawler_data.state = "error" # 状態-> エラー
        crawler_data.save()

    # adminにリダイレクト
    return HttpResponseRedirect('/admin/scrango/crawlerdata/')

class ViewResultView(generic.TemplateView):
    """ 結果ビューjhHTMLを描画 """
    template_name = "scrango/view_result.html"

    def get_context_data(self, **kwargs):
        # コンテキスト取得
        context = super(ViewResultView, self).get_context_data(**kwargs)
        # データ取得
        name = kwargs["name"]
        context['object'] = get_object_or_404(CrawlerData,name=name)

        return context

def get_view_result_js(req, name):
    """ jsonビュアーJSの生成 """
    # データ取得
    crawler_data = get_object_or_404(CrawlerData, name=name)
    last_result = ResultData.objects.filter(crawler=crawler_data).order_by("-datetime")[0] # リザルトとる
    json_data = last_result.json.replace(u"\\",u"\\\\").replace(u"'",u"\\'")

    # JS生成
    with open(TEMPLATE_JSON_JS_PATH) as f :
        # テンプレ読み込む
        js_template = f.read()

    # テンプレートに情報注入
    js_template = js_template.replace(str("{{ JSON }}"), str(json_data))

    return HttpResponse(js_template, content_type="text/javascript; charset=UTF-8")
