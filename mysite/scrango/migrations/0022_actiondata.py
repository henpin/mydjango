# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-22 11:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scrango', '0021_auto_20180519_0155'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=256, null=True, verbose_name='\u8aac\u660e')),
                ('selector', models.CharField(max_length=256, verbose_name='\u64cd\u4f5c\u5bfe\u8c61name\u5c5e\u6027')),
                ('valid', models.BooleanField(default=True, verbose_name='\u6709\u52b9')),
                ('action_type', models.CharField(choices=[('', '\u4f55\u3082\u3057\u306a\u3044'), ('input', '\u5165\u529b'), ('click', '\u30af\u30ea\u30c3\u30af')], default='', max_length=64, verbose_name='\u30a2\u30af\u30b7\u30e7\u30f3\u30bf\u30a4\u30d7')),
                ('content', models.CharField(blank=True, max_length=64, null=True, verbose_name='\u5165\u529b\u5185\u5bb9')),
                ('crawler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scrango.CrawlerData')),
            ],
        ),
    ]