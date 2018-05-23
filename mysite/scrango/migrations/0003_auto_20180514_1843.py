# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-14 09:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrango', '0002_auto_20180514_1804'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scraperdata',
            name='trigger_s',
        ),
        migrations.AddField(
            model_name='scraperdata',
            name='level',
            field=models.CharField(choices=[(1, 1), (2, 2), (3, 3), (4, 4)], default='1', max_length=8, verbose_name='\u53d6\u5f97\u9806\u5e8f'),
        ),
    ]