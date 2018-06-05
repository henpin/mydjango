# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.template.defaultfilters import truncatechars

# User Agents
UA_FF = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0' # FF
UA_CHROME = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36 ' # chrome
UA_IPAD = 'Mozilla/5.0 (iPad; CPU OS 11_2_1 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0 Mobile/15C153 Safari/604.1' # ipad
UA_MAC = 'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; ja-jp) AppleWebKit/85.7 (KHTML, like Gecko) Safari/85.6 ' # safari
UA_ANDROID = 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0' # android
UA_IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_5 like Mac OS X) AppleWebKit/604.5.2 (KHTML, like Gecko) Version/11.0 Mobile/15D5046b Safari/604.1' # iphone


# Create your models here.
class CrawlerData(models.Model):
    """ クローラーデータ """
    STATE_LIST = (
        ("executing","実行中"),
        ("active","正常"),
        ("error","異常"),
    ) # 状態リスト

    REPETITION_INTERVAL_LIST = (
        ("","OFF"),
        ("30","30秒"),
        ("60","1分"),
        ("300","5分"),
        ("600","10分"),
        ("1800","30分"),
        ("3600","1時間"),
        ("10800","3時間"),
        ("21600","6時間"),
        ("43200","12時間"),
    ) # 繰り返し秒数

    SCREENSHOT_SIZE_LIST = (
        ("","OFF"),
        ("(1280px,720px)","スマホサイズ"),
        ("(1280px,980px)","PCサイズ"),
    ) # スクリーンショットサイズ

    NOTIFICATION_LIST = (
        ("","未設定"),
        ("slack","slack"),
        ("chatwork","chatwork"),
    ) # 通知先

    USERAGENT_LIST = (
        (UA_FF,"自動"),
        (UA_FF,"Firefox"),
        (UA_CHROME,"GoogleChrome"),
        (UA_IPAD,"Safari(ipad)"),
        (UA_MAC,"Safari(mac)"),
        (UA_ANDROID,"Firefox(Android)"),
        (UA_IPHONE,"iphone")
    ) # ユーザーエージェントリスト

    name = models.CharField("名前",max_length=255)
    description = models.CharField("説明", blank=True, null=True, max_length=1024)
    url = models.CharField("URL",max_length=512, blank=True)
    state = models.CharField("状態", max_length=64, choices=STATE_LIST, default="active",editable=False) # 初期化フラグ
    repetition = models.CharField("定期実行", max_length=64, choices=REPETITION_INTERVAL_LIST, blank=True) # 繰り返し定義
    screenshot = models.CharField("スクリーンショット", choices=SCREENSHOT_SIZE_LIST ,max_length=64, blank=True) # 必須ブーリアン
    notification = models.CharField("通知先", choices=NOTIFICATION_LIST ,max_length=64, blank=True) # 通知先
    last_execute_time = models.DateTimeField("最近の実行日時", null=True, blank=True, editable=False) # 実行日時
    user_agent = models.CharField("ユーザーエージェント", choices=USERAGENT_LIST ,max_length=255, default=UA_FF) # 通知先
    #proxy = models.CharField("プロキシサーバー", max_length=256, blank=True, null=True) # プロキシサーバー

    def __unicode__(self):
        return self.name

    def short_url(self):
        """ 短いURL """
        return truncatechars(self.url, 80)


class ActionData(models.Model):
    """ アクションデータ"""
    ACTION_TYPE_LIST = (
        ("","何もしない"),
        ("input","入力"),
        ("click","クリック"),
        ("reload","リロード"),
        ("enter_iframe","iframeに入る"),
        ("drag_and_drop","ドラッグアンドドロップ"),
        ("upload_file","ファイルアップロード")
    )
    crawler = models.ForeignKey(CrawlerData, on_delete=models.CASCADE) # クローラーに対してフォーリングキー
    selector = models.CharField("操作対象name属性", blank=True, null=True, max_length=255)
    action_type = models.CharField("アクションタイプ", max_length=64, choices=ACTION_TYPE_LIST, default="") # アクションの詳細
    content = models.CharField("入力内容", max_length=64, blank=True, null=True) # 入力内容
    valid = models.BooleanField("有効", default=True) # 有効/無効
    description = models.CharField("説明", blank=True, null=True, max_length=255)

    def __unicode__(self):
        return self.description or u"操作コマンド"


class ScraperData(models.Model):
    """ スクレイパーデータ"""
    TARGET_LIST = (
        ("","見つけるだけ"),
        ("html","HTML"),
        ("text","本文"),
        ("src","src属性値"),
        ("href","href属性地"),
    ) # 取得コンテンツチョイス

    selector = models.CharField("CSSセレクタ",max_length=255)
    target = models.CharField("取得対象", max_length=64, choices=TARGET_LIST, default="html", blank=True, null=True) # 属性
    crawler = models.ForeignKey(CrawlerData, on_delete=models.CASCADE) # クローラーに対してフォーリングキー
    master_scraper = models.ForeignKey("self",verbose_name="これを見つけたら実行",null=True,blank=True, on_delete=models.PROTECT) # 従属的スクレイパ
    name = models.CharField("名前",max_length=255)
    crawler_name = models.CharField("クローラー名",max_length=255,blank=True) # 再帰的クローラー名
    valid = models.BooleanField("有効", default=True) # 有効/無効

    def __unicode__(self):
        return self.name

class ResultData(models.Model):
    """ スクレイピング結果 """
    RESULT_LIST = (
        ("success","正常終了"),
        ("failure","失敗"),
    )

    crawler = models.ForeignKey(CrawlerData, on_delete=models.CASCADE) # 生成元クローラー
    datetime = models.DateTimeField("実行時間",default=timezone.now) # 実行時間
    json = models.TextField(blank=True, editable=True) # 解析結果JSON
    result = models.CharField("可否", max_length=64, choices=RESULT_LIST, default="", blank=True) # 属性
    screenshot = models.ImageField(upload_to="images/",null=True,blank=True)

    class Meta:
        ordering = ('-datetime',)

    def __unicode__(self):
        return str(self.datetime)

