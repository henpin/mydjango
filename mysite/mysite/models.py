# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class GeneralModel(models.Model):
    """ 汎用モデル """
    created_at = models.DateTimeField("作成日時", auto_now=True)
    created_by = models.ForeignKey(User, blank=True, null=True, editable=False)
    #updated_at = models.DateTimeField(u'更新日時', auto_now=True)

    class Meta:
        abstract = True

class GeneralLogModel(models.Model):
    """ ログモデル"""
    RESULT_LIST = (
        ("success","正常終了"),
        ("failure","失敗"),
    )

    result = models.CharField("可否", max_length=64, choices=RESULT_LIST, default="", blank=True) # 属性
    datetime = models.DateTimeField("時刻",default=timezone.now) # 実行時間
    log = models.TextField(blank=True,null=True) # ログデータ

    class Meta:
        abstract = True
