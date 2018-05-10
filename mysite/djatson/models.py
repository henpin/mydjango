# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class URLData(models.Model):
    """ URL情報 """
    STATE_LIST = (
        ("pending","初期化待ち"),
        ("initializing","初期化中"),
        ("active","正常"),
        ("error","異常"),
    )
    
    url = models.CharField("URL",max_length=512)
    name = models.CharField("名前",max_length=256)
    description = models.CharField("説明",max_length=256,default="") # 説明
    selector = models.CharField("対象CSSセレクタ(オプション)",blank=True,max_length=128, editable=False) # 解析対象 : 廃止予定
    state = models.CharField("状態", max_length=64, choices=STATE_LIST, default="pending",editable=False) # 初期化フラグ
    json = models.TextField(blank=True, editable=False) # 解析済みJSONデータ
    ws_id = models.CharField("ワークスペースID",max_length=512,default="",editable=False) # WatsonワークスペースID

    def __unicode__(self):
        return self.name
