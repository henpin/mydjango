# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Question(models.Model):
    """" 質問データモデル """
    question_text = models.CharField(max_length=256) # 質問文字列
    pub_date = models.DateTimeField() # 投票日
    
    def __str__(self):
        return self.question_text
        

class Choice(models.Model):
    """ 選択データモデル """
    question = models.ForeignKey(Question, on_delete=models.CASCADE) # PK: 質問
    choice_text = models.CharField(max_length=256) # 選択対象
    votes = models.IntegerField() # 投票数

    def __str__(self):
        return self.choice_text
