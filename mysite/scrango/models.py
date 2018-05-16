# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

# Create your models here.
class CrawlerData(models.Model):
    """ クローラーデータ """
    ATTR_LIST = (
        ("master","マスター"),
        ("slave","スレーブ"),
    ) # 属性

    STATE_LIST = (
        ("pending","初期化待ち"),
        ("initializing","初期化中"),
        ("active","正常"),
        ("error","異常"),
    ) # 状態リスト

    attribute = models.CharField("属性", max_length=64, choices=ATTR_LIST, default="master") # 属性
    name = models.CharField("名前",max_length=256)
    url = models.CharField("URL",max_length=512, blank=True)
    state = models.CharField("状態", max_length=64, choices=STATE_LIST, default="active",editable=False) # 初期化フラグ

    def __unicode__(self):
        return self.name

class ScraperData(models.Model):
    """ スクレイパーデータ"""
    TARGET_LIST = (
        ("html","HTML"),
        ("text","本文"),
        ("src","src属性値"),
        ("href","href属性地"),
    ) # 取得コンテンツチョイス

    selector = models.CharField("CSSセレクタ",max_length=256)
    target = models.CharField("取得対象", max_length=64, choices=TARGET_LIST, default="html") # 属性
    crawler = models.ForeignKey(CrawlerData) # クローラーに対してフォーリングキー
    master_scraper = models.ForeignKey("self",verbose_name="これを見つけたら実行",null=True,blank=True) # 従属的スクレイパ
    name = models.CharField("名前",max_length=256)
    crawler_name = models.CharField("クローラー名",max_length=256,blank=True) # 再帰的クローラー名

    def __unicode__(self):
        return self.name

class ResultData(models.Model):
    """ スクレイピング結果 """
    RESULT_LIST = (
        ("success","正常終了"),
        ("failure","失敗"),
    )

    crawler = models.ForeignKey(CrawlerData) # 生成元クローラー
    datetime = models.DateTimeField("実行時間",default=timezone.now) # 実行時間
    json = models.TextField(blank=True, editable=True) # 解析結果JSON
    result = models.CharField("可否", max_length=64, choices=RESULT_LIST, default="", blank=True) # 属性

    class Meta:
        ordering = ('-datetime',)

    def __unicode__(self):
        return str(self.datetime)

