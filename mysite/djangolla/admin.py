# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# general
from django.shortcuts import render
from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse
# Models
from .models import FormData, InputData, LogManageData, LogData
# modules
from .apps import gen_url
# extenstions
from django_admin_row_actions import AdminRowActionsMixin


"""
Admin画面
"""


def display_html(modelAdmin, req, qs):
    """ デモHTMLをリクエスト """
    # クエリセットから始めの値しゅとく
    item = qs[0]

    # API利用でフォーム名からurl生成
    url = gen_url("html",item.form_name)

    # リダイレクトする
    return HttpResponseRedirect(url)
display_html.short_description = "デモページ生成"


def display_js(modelAdmin, req, qs):
    """ デモJSをリクエスト """
    # クエリセットから始めの値しゅとく
    item = qs[0]

    # API利用でフォーム名からurl生成
    url = gen_url("js",item.form_name)

    # リダイレクトする
    return HttpResponseRedirect(url)
display_js.short_description = "JS生成"


def display_replay(modelAdmin, req, qs):
    """ リプレイ画面に飛ぶ """
    # 値取得
    item = qs[0]

    # API利用でフォーム名からurl生成
    url = gen_url("replay_html",item.uuid)

    # リダイレクトする
    return HttpResponseRedirect(url)
display_replay.short_description = "リプレイ再生"


class InputDataInline(admin.TabularInline):
    """ Input入力欄を並べるやつ """
    model = InputData
    extra = 3


class FormDataAdmin(AdminRowActionsMixin, admin.ModelAdmin):
    """ フォームデータ編集Admin """
    # アクション
    actions = [
        display_html,
        display_js,
    ]
    # 並べる
    inlines = [InputDataInline]
    #list_display = ("form_name")

    def get_row_actions(self, item):
        """ プラグイン用行アクション """
        # API利用でフォーム名からurl生成
        url = gen_url("html",item.form_name)
        url_forJS = gen_url("js",item.form_name)

        # 行埋め込みアクション
        row_actions = [
            {
                'label': 'デモ画面で確認',
                'url': url
            },
            {
                'label': 'JS生成',
                'url': url_forJS
            }
        ]

        return row_actions


class LogDataInline(admin.TabularInline):
    """ ログデータまとめる"""
    model = LogData

class LogManageDataAdmin(AdminRowActionsMixin, admin.ModelAdmin):
    """ ログマネージャデータAdmin"""
    # アクション
    actions = [
        display_replay
    ]
    # 並べる
    inlines = [LogDataInline]
    list_display = ("uuid","datetime","form")
    # ソート順
    ordering = ["-datetime"]

    def get_row_actions(self, item):
        """ プラグイン用行アクション """
        # API利用でフォーム名からurl生成
        url = gen_url("replay_html",item.uuid)
        row_actions = [
            {
                'label': 'プレイバック再生',
                'url': url
            }
        ]

        return row_actions
        
    
# Register your models here.
admin.site.register(FormData, FormDataAdmin)
admin.site.register(LogManageData, LogManageDataAdmin)

# ヘッダ編集
admin.AdminSite.site_header = u"Djangollaデモサイト"
