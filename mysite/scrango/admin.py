# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# general
from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse
# Models
from .models import CrawlerData, ScraperData, ResultData
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

class CrawlerDataAdmin(AdminRowActionsMixin, admin.ModelAdmin):
    """ クローラーデータAdmin """
    # アクション
    actions = [
    ]
    # 並べる
    inlines = [
        ScraperDataInline,
        ResultDataInline
        ]
    #list_display = ("form_name")

    def get_row_actions(self, item):
        """ プラグイン用行アクション """
        url = gen_url("scrape",item.name)
        # 行埋め込みアクション
        row_actions = [
            {
                'label': 'スクレピング開始',
                'url': url
            },
        ]

        return row_actions


# Register your models here.
admin.site.register(CrawlerData, CrawlerDataAdmin)
