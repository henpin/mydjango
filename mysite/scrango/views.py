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
from .models import ScraperData, ScraperInfoData, ResultData, ChatAPIData
from .models import WebAPIData, WebAPIResultData, WebAPIParameterData, WebAPIHttpHeaderParameterData

import tasks

from exception_utils import WebAPIException


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
    json_data = last_result.result_data.replace(u"\\",u"\\\\").replace(u"'",u"\\'")

    # JS生成
    with open(TEMPLATE_JSON_JS_PATH) as f :
        # テンプレ読み込む
        js_template = f.read()

    # テンプレートに情報注入
    js_template = js_template.replace(str("{{ JSON }}"), str(json_data))

    return HttpResponse(js_template, content_type="text/javascript; charset=UTF-8")


# API
class ScrapeAPIVS(viewsets.ViewSet):
    """ スクレイピングAPIJビューセット"""
    def retrieve(self, request, pk=None):
        """ Getメソッド処理"""
        # データ取得
        scraper_data = get_object_or_404(ScraperData, uuid=pk)

        # スクレイピング開始
        result = tasks.do_scrape(scraper_data)

        # JSONなのでそのまま返す
        return Response(result)

    @action(methods=['post'], detail=True)
    def inject(self,request,pk=None):
        """ POST処理 """
        # POSTからデータ抜く
        url = request.POST.get("url")

        # データ取得
        scraper_data = get_object_or_404(ScraperData, uuid=pk) # URL指定

        # スクレイピング開始
        result = tasks.do_scrape(scraper_data, _url=url)

        # JSONなのでそのまま返す
        return Response(result)


class NotificationTestAPIVS(viewsets.ViewSet):
    """ 通知テストAPI """
    def retrieve(self, request, pk=None):
        """ Getメソッド処理"""
        # データ取得
        chatapi_data = get_object_or_404(ChatAPIData, uuid=pk).convert2entity() # 通知先 : 具象クラスに落とす

        # 通知
        try :
            # 通知
            tasks.send_notification(chatapi_data,"test message from Scrango",None)
            return Response("通知に成功しました")
            
        except WebAPIException :
            return Response("通知に失敗しました")
            

class CallWebAPIVS(viewsets.ViewSet):
    """ webAPI呼び出しVS """
    def retrieve(self, request, pk=None):
        """ Getメソッド処理"""
        # データ取得
        webapi_data = get_object_or_404(WebAPIData, uuid=pk) # apiデータ抜く

        # 直接関数として呼ぶ
        result_data = tasks.call_webapi(webapi_data)

        # 呼び出し結果を返す
        return Response(result_data.result_data)

