# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-06-05 01:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangolla', '0003_auto_20180422_0005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formdata',
            name='form_name',
            field=models.CharField(max_length=255, verbose_name='\u30d5\u30a9\u30fc\u30e0\u540d'),
        ),
        migrations.AlterField(
            model_name='inputdata',
            name='input_name',
            field=models.CharField(max_length=255, verbose_name='name\u5c5e\u6027'),
        ),
        migrations.AlterField(
            model_name='logdata',
            name='input_name',
            field=models.CharField(max_length=255, verbose_name='name\u5c5e\u6027'),
        ),
        migrations.AlterField(
            model_name='logdata',
            name='input_value',
            field=models.CharField(max_length=255, verbose_name='\u5165\u529b\u5024'),
        ),
    ]
