# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from mysite.models import GeneralModel, GeneralLogModel
from django.db import models
import uuid

# Create your models here.
class CrawlerData(GeneralModel):
    """ URL情報 """
    STATE_LIST = (
        ("pending","初期化待ち"),
        ("crawling","クロール中"),
        ("active","正常"),
        ("error","異常"),
    )
    
    url = models.URLField("URL")
    name = models.CharField("名前",max_length=255)
    keyword = models.CharField("キーワード",max_length=255)
    #selector = models.CharField("対象CSSセレクタ(オプション)",blank=True,max_length=128, editable=False) # 解析対象 : 廃止予定
    state = models.CharField("状態", max_length=64, choices=STATE_LIST, default="pending",editable=False) # 初期化フラグ
    ws_id = models.CharField("ワークスペースID",max_length=512,default="",editable=False) # WatsonワークスペースID
    limit = models.PositiveSmallIntegerField("最大クロール数",default=0) # 最大クロール数
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    def __unicode__(self):
        return self.name

class DjatsonLogData(GeneralLogModel):
    """ ジャトソンデータ """
    crawler = models.ForeignKey(CrawlerData, on_delete=models.CASCADE) # クローラーに対してフォーリングキー
    json = models.TextField(blank=True, editable=False, default="") # 解析済みJSONデータ

class CrawlingLogData(GeneralLogModel):
    """ クロールログ """
    crawler = models.ForeignKey(CrawlerData, on_delete=models.CASCADE) # クローラーに対してフォーリングキー
    
class HtmlData(models.Model):
    """ HTMLデータ"""
    crawlinglog = models.ForeignKey(CrawlingLogData, on_delete=models.CASCADE) # クロールログに対して保存
    url = models.URLField("URL")
    title = models.CharField("タイトル",max_length=255)
    html = models.TextField(blank=True, null=True) # HTMLデータ

