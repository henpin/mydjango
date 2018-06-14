# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-06-14 06:36
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CrawlerData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='\u4f5c\u6210\u65e5\u6642')),
                ('url', models.URLField(verbose_name='URL')),
                ('name', models.CharField(max_length=255, verbose_name='\u540d\u524d')),
                ('state', models.CharField(choices=[('pending', '\u521d\u671f\u5316\u5f85\u3061'), ('crawling', '\u30af\u30ed\u30fc\u30eb\u4e2d'), ('active', '\u6b63\u5e38'), ('error', '\u7570\u5e38')], default='pending', editable=False, max_length=64, verbose_name='\u72b6\u614b')),
                ('ws_id', models.CharField(default='', editable=False, max_length=512, verbose_name='\u30ef\u30fc\u30af\u30b9\u30da\u30fc\u30b9ID')),
                ('limit', models.PositiveSmallIntegerField(default=0, verbose_name='\u6700\u5927\u30af\u30ed\u30fc\u30eb\u6570')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CrawlingLogData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.CharField(blank=True, choices=[('success', '\u6b63\u5e38\u7d42\u4e86'), ('failure', '\u5931\u6557')], default='', max_length=64, verbose_name='\u53ef\u5426')),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\u6642\u523b')),
                ('log', models.TextField(blank=True, null=True)),
                ('crawler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='djatson.CrawlerData')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DjatsonLogData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.CharField(blank=True, choices=[('success', '\u6b63\u5e38\u7d42\u4e86'), ('failure', '\u5931\u6557')], default='', max_length=64, verbose_name='\u53ef\u5426')),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\u6642\u523b')),
                ('log', models.TextField(blank=True, null=True)),
                ('json', models.TextField(blank=True, default='', editable=False)),
                ('crawler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='djatson.CrawlerData')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HtmlData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(verbose_name='URL')),
                ('html', models.TextField(blank=True, null=True)),
                ('crawlinglog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='djatson.CrawlingLogData')),
            ],
        ),
    ]
