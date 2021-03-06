# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-20 13:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FormData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_name', models.CharField(max_length=256, verbose_name='\u30d5\u30a9\u30fc\u30e0\u540d')),
            ],
        ),
        migrations.CreateModel(
            name='InputData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_name', models.CharField(max_length=256, verbose_name='name\u5c5e\u6027')),
                ('input_type', models.CharField(choices=[('email', 'e\u30e1\u30fc\u30eb\u30a2\u30c9\u30ec\u30b9'), ('mail', '\u30e1\u30fc\u30eb\u30a2\u30c9\u30ec\u30b9'), ('url', 'URL'), ('date', '\u65e5\u4ed8'), ('digits', '\u6570\u5b57'), ('creditcard', '\u30af\u30ec\u30b8\u30c3\u30c8\u30ab\u30fc\u30c9'), ('hiragana', '\u3072\u3089\u304c\u306a'), ('katakana', '\u30ab\u30bf\u30ab\u30ca'), ('alphanum', '\u30a2\u30eb\u30d5\u30a1\u30d9\u30c3\u30c8/\u6570\u5b57'), ('telnum', '\u96fb\u8a71\u756a\u53f7'), ('postnum', '\u90f5\u4fbf\u756a\u53f7')], max_length=64, verbose_name='\u5165\u529b\u30bf\u30a4\u30d7')),
                ('require', models.BooleanField(default=True, verbose_name='\u5fc5\u9808')),
                ('error_msg', models.CharField(max_length=512, verbose_name='\u30a8\u30e9\u30fc\u30e1\u30c3\u30bb\u30fc\u30b8')),
                ('parent_form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='djangolla.FormData')),
            ],
        ),
        migrations.CreateModel(
            name='LogData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(verbose_name='\u53d7\u4fe1\u6642\u9593')),
                ('input_name', models.CharField(max_length=256, verbose_name='name\u5c5e\u6027')),
                ('input_value', models.CharField(max_length=256, verbose_name='\u5165\u529b\u5024')),
            ],
        ),
        migrations.CreateModel(
            name='LogManageData',
            fields=[
                ('uuid', models.CharField(max_length=1024, primary_key=True, serialize=False, verbose_name='UUID')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='djangolla.FormData')),
            ],
        ),
        migrations.AddField(
            model_name='logdata',
            name='uuid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='djangolla.LogManageData'),
        ),
    ]
