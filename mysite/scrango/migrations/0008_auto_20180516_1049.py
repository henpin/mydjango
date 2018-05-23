# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-16 01:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrango', '0007_resultdata_result'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='resultdata',
            options={'ordering': ('-datetime',)},
        ),
        migrations.AddField(
            model_name='crawlerdata',
            name='state',
            field=models.CharField(choices=[('pending', '\u521d\u671f\u5316\u5f85\u3061'), ('initializing', '\u521d\u671f\u5316\u4e2d'), ('active', '\u6b63\u5e38'), ('error', '\u7570\u5e38')], default='active', editable=False, max_length=64, verbose_name='\u72b6\u614b'),
        ),
        migrations.AlterField(
            model_name='resultdata',
            name='json',
            field=models.TextField(blank=True),
        ),
    ]