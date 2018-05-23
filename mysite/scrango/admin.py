# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# general
from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse
# Models
from .models import CrawlerData, ScraperData, ResultData, ActionData
# modules
from .apps import gen_url
# extenstions
from django_admin_row_actions import AdminRowActionsMixin

# Register your models here.
class ScraperDataInline(admin.TabularInline):
    """ スクレイパーデータテーブル """
    model = ScraperData
    extra = 3

class ResultDataInline(admin.TabularInline):
    """ スクレイパーデータテーブル """
    model = ResultData
    extra = 0
    max_num = 20

class ActionDataInline(admin.TabularInline):
    """ アクションデータテーブル"""
    model = ActionData
    extra = 5


class CrawlerDataAdmin(AdminRowActionsMixin, admin.ModelAdmin):
    """ クローラーデータAdmin """
    # アクション
    actions = [
    ]
    # 並べる
    inlines = [
        ScraperDataInline,
        ResultDataInline,
        ActionDataInline
        ]
    list_display = ("name","description","short_url","state","repetition","screenshot","notification","last_execute_time")

    def get_row_actions(self, item):
        """ プラグイン用行アクション """
        url_for_scrape = gen_url("scrape",item.name)
        url_for_view = gen_url("view_result",item.name)
        # 行埋め込みアクション
        row_actions = [
            {
                'label': 'スクレピング開始',
                'url': url_for_scrape
            },
            {
                'label': '結果を見る',
                'url': url_for_view
            }
        ]

        return row_actions


# Register your models here.
admin.site.register(CrawlerData, CrawlerDataAdmin)