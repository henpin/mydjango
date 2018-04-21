# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse

# Register your models here.
from .models import FormData, InputData, LogManageData, LogData

from .apps import gen_url

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


class FormDataAdmin(admin.ModelAdmin):
    """ フォームデータ編集Admin """
    # アクション
    actions = [
        display_html,
        display_js,
    ]
    # 並べる
    inlines = [InputDataInline]
    #list_display = ("form_name")


class LogDataInline(admin.TabularInline):
    """ ログデータまとめる"""
    model = LogData

class LogManageDataAdmin(admin.ModelAdmin):
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
    
# Register your models here.
admin.site.register(FormData, FormDataAdmin)
admin.site.register(LogManageData, LogManageDataAdmin)

# ヘッダ編集
admin.AdminSite.site_header = u"Djangollaデモサイト"
