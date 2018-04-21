# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

"""
ジャンゴラモデル
"""

# Create your models here.
class FormData(models.Model):
    """ フォームそのもの"""
    form_name = models.CharField("フォーム名",max_length=256) # フォーム名

    def __unicode__(self):
        return self.form_name


class InputData(models.Model):
    """ 個々のInputでーた"""
    INPUT_TYPE = (
        ("email","eメールアドレス"),
        ("mail","メールアドレス"),
        ("url","URL"),
        ("date","日付"),
        ("digits","数字"),
        ("creditcard","クレジットカード"),
        ("hiragana","ひらがな"), # 以下ユーザー定義バリデーション
        ("katakana","カタカナ"),
        ("alphanum","アルファベット/数字"),
        ("telnum","電話番号"),
        ("postnum","郵便番号"),
    ) # input欄の種類
    parent_form = models.ForeignKey(FormData) # フォームが親
    input_name = models.CharField("name属性", max_length=256) # input名
    input_type = models.CharField("入力タイプ", max_length=64, choices=INPUT_TYPE) # 選択
    require = models.BooleanField("必須", default=True) # 必須ブーリアン
    error_msg = models.CharField("エラーメッセージ", max_length=512) # エラーメッセージ

    def __unicode__(self):
        return self.input_name
    
class LogManageData(models.Model):
    """ ログマネージャ """
    uuid = models.CharField("UUID", max_length=1024, primary_key=True) # 一意のログ管理ID:Ajaxで利用
    form = models.ForeignKey(FormData) # フォーム
    datetime = models.DateTimeField("受信時間",default=timezone.now) # 受信時間

    def __unicode__(self):
        return self.uuid

class LogData(models.Model):
    """ 入力ログ """
    manager = models.ForeignKey(LogManageData) # ログマネージャ
    datetime = models.DateTimeField("受信時間",default=timezone.now) # 受信時間
    input_name = models.CharField("name属性", max_length=256) # input名
    input_value = models.CharField("入力値", max_length=256) # input値

    def __unicode__(self):
        return str(self.datetime)

