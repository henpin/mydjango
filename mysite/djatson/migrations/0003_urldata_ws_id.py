# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-03 11:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djatson', '0002_auto_20180503_2037'),
    ]

    operations = [
        migrations.AddField(
            model_name='urldata',
            name='ws_id',
            field=models.CharField(default='', editable=False, max_length=512, verbose_name='\u30ef\u30fc\u30af\u30b9\u30da\u30fc\u30b9ID'),
        ),
    ]
