# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-06-05 01:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrango', '0028_crawlerdata_user_agent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actiondata',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='\u8aac\u660e'),
        ),
        migrations.AlterField(
            model_name='actiondata',
            name='selector',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='\u64cd\u4f5c\u5bfe\u8c61name\u5c5e\u6027'),
        ),
        migrations.AlterField(
            model_name='crawlerdata',
            name='name',
            field=models.CharField(max_length=255, verbose_name='\u540d\u524d'),
        ),
        migrations.AlterField(
            model_name='crawlerdata',
            name='user_agent',
            field=models.CharField(choices=[('Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0', '\u81ea\u52d5'), ('Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0', 'Firefox'), ('Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36 ', 'GoogleChrome'), ('Mozilla/5.0 (iPad; CPU OS 11_2_1 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0 Mobile/15C153 Safari/604.1', 'Safari(ipad)'), ('Mozilla/5.0 (Macintosh; U; PPC Mac OS X; ja-jp) AppleWebKit/85.7 (KHTML, like Gecko) Safari/85.6 ', 'Safari(mac)'), ('Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0', 'Firefox(Android)'), ('Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_5 like Mac OS X) AppleWebKit/604.5.2 (KHTML, like Gecko) Version/11.0 Mobile/15D5046b Safari/604.1', 'iphone')], default='Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0', max_length=255, verbose_name='\u30e6\u30fc\u30b6\u30fc\u30a8\u30fc\u30b8\u30a7\u30f3\u30c8'),
        ),
        migrations.AlterField(
            model_name='scraperdata',
            name='crawler_name',
            field=models.CharField(blank=True, max_length=255, verbose_name='\u30af\u30ed\u30fc\u30e9\u30fc\u540d'),
        ),
        migrations.AlterField(
            model_name='scraperdata',
            name='name',
            field=models.CharField(max_length=255, verbose_name='\u540d\u524d'),
        ),
        migrations.AlterField(
            model_name='scraperdata',
            name='selector',
            field=models.CharField(max_length=255, verbose_name='CSS\u30bb\u30ec\u30af\u30bf'),
        ),
    ]