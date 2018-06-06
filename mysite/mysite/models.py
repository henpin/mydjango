# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class GeneralModel(models.Model):
    """ 汎用モデル """
    created_at = models.DateTimeField("作成日時", auto_now=True)
    created_by = models.ForeignKey(User, blank=True, null=True)
    #updated_at = models.DateTimeField(u'更新日時', auto_now=True)

    class Meta:
        abstract = True
