# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# general
from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse
# modules
from .apps import gen_url

# Models
from .models import CrawlerData, DjatsonLogData, CrawlingLogData, HtmlData

# extenstions
from django_admin_row_actions import AdminRowActionsMixin



# Register your models here.
class DjatsonLogDataInline(admin.TabularInline):
    """ ジャトソンログ """
    model = DjatsonLogData

class CrawlingLogDataInline(admin.TabularInline):
    """ クローリングログ """
    model = CrawlingLogData

class HtmlDataInline(admin.TabularInline):
    """ HTMLデータ """
    model = HtmlData


class CrawlerDataAdmin(AdminRowActionsMixin, admin.ModelAdmin):
    """ URLデータのアド民 """
    # アクション
    actions = [
    ]
    # 並べる
    list_display = ("url","name","state","ws_id")
    # 並べる
    inlines = [
        DjatsonLogDataInline,
        CrawlingLogDataInline
        ]

    def get_row_actions(self, item):
        """ プラグイン用行アクション """
        # url生成
        url_for_json = gen_url("view_json",item.name)
        url_for_chat = gen_url("chat",item.name)
        url_for_initialize = gen_url("initialize",item.name)
        row_actions = [
            {
                'label': '解析結果を表示',
                'url' : url_for_json
            },
            {
                'label': 'watsonを初期化',
                'url' : url_for_initialize
            },
            {
                'label': 'watsonとしゃべる',
                'url' : url_for_chat
            }
        ]

        return row_actions




# Global admin settings
admin.site.register(CrawlerData, CrawlerDataAdmin)
