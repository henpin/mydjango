# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# general
from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse
# Models
from .models import ScraperData, ScraperInfoData, ResultData, ActionData
from .models import SlackAPIData, ChatworkAPIData, TwitterAPIData, LineAPIData
from .models import WebAPIData, WebAPIResultData, WebAPIParameterData, WebAPIHttpHeaderParameterData
# modules
from .apps import gen_url
# extenstions
from django_admin_row_actions import AdminRowActionsMixin

# Register your models here.
class ScraperInfoDataInline(admin.TabularInline):
    """ スクレイパーデータテーブル """
    model = ScraperInfoData
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


class ScraperDataAdmin(AdminRowActionsMixin, admin.ModelAdmin):
    """ クローラーデータAdmin """
    # アクション
    actions = [
    ]
    # 並べる
    inlines = [
        ScraperInfoDataInline,
        ActionDataInline,
        ResultDataInline,
        ]
    list_display = ("name","short_url","state","repetition","screenshot","notification","last_execute_time")

    def get_row_actions(self, item):
        """ プラグイン用行アクション """
        url_for_scrape = gen_url("scrape",str(item.uuid))
        url_for_view = gen_url("view_result",str(item.uuid))
        url_for_api = gen_url("api/scrape",str(item.uuid))
        # 行埋め込みアクション
        row_actions = [
            {
                'label': 'スクレピング開始',
                'url': url_for_scrape
            },
            {
                'label': '結果を見る',
                'url': url_for_view
            },
            {
                'label': 'WebAPI呼び出し',
                'url': url_for_api
            }
        ]

        return row_actions


class ChatAPIDataAdmin(AdminRowActionsMixin, admin.ModelAdmin):
    """ チャット連携基底 """
    def get_row_actions(self, item):
        """ プラグイン用行アクション """
        url_for_test = gen_url("api/notification_test",str(item.uuid))
        # 行埋め込みアクション
        row_actions = [
            {
                'label': 'テスト送信',
                'url': url_for_test
            },
        ]

        return row_actions


class SlackAPIDataAdmin(ChatAPIDataAdmin):
    """ スラックAPI情報登録 """
    pass

class ChatworkAPIDataAdmin(ChatAPIDataAdmin):
    """ チャットワークAPI情報登録"""
    pass

class TwitterAPIDataAdmin(ChatAPIDataAdmin):
    """ ツイッターAPI情報登録"""
    pass

class LineAPIDataAdmin(ChatAPIDataAdmin):
    """ ラインAPI情報登録"""
    pass


class WebAPIParameterDataInline(admin.TabularInline):
    """ ウェッブAPIパラミータデータ"""
    model = WebAPIParameterData
    extra = 3

class WebAPIHttpHeaderParameterDataInline(admin.TabularInline):
    """ ウェッブAPIHttpヘッダデータ"""
    model = WebAPIHttpHeaderParameterData
    extra = 3

class WebAPIResultDataInline(admin.TabularInline):
    """ ウェッブAPI結果データ"""
    model = WebAPIResultData
    extra = 0

class WebAPIDataAdmin(AdminRowActionsMixin, admin.ModelAdmin):
    """ ウェッブAPIデータ"""
    # 並べる
    inlines = [
        WebAPIParameterDataInline,
        WebAPIResultDataInline,
        WebAPIHttpHeaderParameterDataInline
        ]
    list_display = ("name","repetition","notification","last_execute_time")

    def get_row_actions(self, item):
        """ プラグイン用行アクション """
        url_for_call = gen_url("api/call_webapi",str(item.uuid))
        # 行埋め込みアクション
        row_actions = [
            {
                'label': 'APIを呼び出す',
                'url': url_for_call
            },
        ]

        return row_actions



# Register your models here.
admin.site.register(ScraperData, ScraperDataAdmin)
admin.site.register(SlackAPIData, SlackAPIDataAdmin)
admin.site.register(ChatworkAPIData, ChatworkAPIDataAdmin)
admin.site.register(TwitterAPIData, TwitterAPIDataAdmin)
admin.site.register(LineAPIData, LineAPIDataAdmin)
admin.site.register(WebAPIData, WebAPIDataAdmin)

