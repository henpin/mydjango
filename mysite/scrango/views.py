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
from .models import ScraperData, ScraperInfoData, ResultData

import tasks

# JS template file
TEMPLATE_JSON_JS_PATH = os.path.dirname(os.path.abspath(__file__)) + '/static/view_result.js'

# Create your views here.
def do_scrape(req,_uuid):
    """ スクレイピングする """
    # データ取得
    scraper_data = get_object_or_404(ScraperData, uuid=_uuid)

    # 状態変遷
    if scraper_data.url :
        # 状態変遷
        scraper_data.state = "executing" # 状態-> エラー
        scraper_data.save()
        # スクレイピング開始
        tasks.do_scrape.delay(scraper_data)
    else :
        # 状態変遷
        scraper_data.state = "error" # 状態-> エラー
        scraper_data.save()

    # adminにリダイレクト
    return HttpResponseRedirect('/admin/scrango/scraperdata/')

class ViewResultView(generic.TemplateView):
    """ 結果ビューjhHTMLを描画 """
    template_name = "scrango/view_result.html"

    def get_context_data(self, **kwargs):
        # コンテキスト取得
        context = super(ViewResultView, self).get_context_data(**kwargs)
        # データ取得
        _uuid = kwargs["_uuid"]
        context['object'] = get_object_or_404(ScraperData,uuid=_uuid)

        return context

def get_view_result_js(req, _uuid):
    """ jsonビュアーJSの生成 """
    # データ取得
    scraper_data = get_object_or_404(ScraperData, uuid=_uuid)
    last_result = ResultData.objects.filter(scraper=scraper_data).order_by("-datetime")[0] # リザルトとる
    json_data = last_result.json.replace(u"\\",u"\\\\").replace(u"'",u"\\'")

    # JS生成
    with open(TEMPLATE_JSON_JS_PATH) as f :
        # テンプレ読み込む
        js_template = f.read()

    # テンプレートに情報注入
    js_template = js_template.replace(str("{{ JSON }}"), str(json_data))

    return HttpResponse(js_template, content_type="text/javascript; charset=UTF-8")


# API
class ScrapeAPIViewSet(viewsets.ViewSet):
    """ スクレイピングAPIJビューセット"""
    def retrieve(self, request, pk=None):
        """ Getメソッド処理"""
        # データ取得
        scraper_data = get_object_or_404(ScraperData, uuid=pk)

        # スクレイピング開始
        result = tasks.do_scrape(scraper_data)

        # JSONなのでそのまま返す
        return Response(result)


