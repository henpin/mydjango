# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class FormData(models.Model):
    """ フォームそのもの"""
    form_name = models.CharField("フォーム名",max_length=256) # フォーム名

    def __unicode__(self):
        return self.form_name

class InputData(models.Model):
    """ 個々のInputでーた"""
    INPUT_TYPE = (
        ("kana","ひらがな"),
        ("katakana","カタカナ"),
        ("kanji","漢字"),
        ("alpha","アルファベット"),
        ("num","数字"),
        ("phone","電話番号"),
        ("mail","メールアドレス")
    ) # input欄の種類
    parent_form = models.ForeignKey(FormData) # フォームが親
    input_name = models.CharField("name属性", max_length=256) # input名
    input_type = models.CharField("入力タイプ", max_length=64, choices=INPUT_TYPE) # 選択

    def __unicode__(self):
        return self.input_name
    
