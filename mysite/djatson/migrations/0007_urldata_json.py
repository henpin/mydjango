# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-07 05:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djatson', '0006_auto_20180505_2322'),
    ]

    operations = [
        migrations.AddField(
            model_name='urldata',
            name='json',
            field=models.TextField(blank=True),
        ),
    ]