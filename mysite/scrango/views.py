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

# Create your views here.
def do_scrape(req,name):
    """ スクレイピングする """
    # データ取得
    crawler_data = get_object_or_404(CrawlerData, name=name)

    # スクレイピング開始
    tasks.do_scrape.delay(crawler_data)

    # adminにリダイレクト
    return HttpResponseRedirect('/admin/scrango/crawlerdata/')
