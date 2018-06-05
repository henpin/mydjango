# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-06-05 08:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scrango', '0030_auto_20180605_1055'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatAPIData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(blank=True, max_length=128, null=True, verbose_name='\u30e6\u30fc\u30b6\u30fc\u540d')),
            ],
        ),
        migrations.AlterField(
            model_name='crawlerdata',
            name='notification',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='scrango.ChatAPIData'),
        ),
        migrations.CreateModel(
            name='ChatworkAPIData',
            fields=[
                ('chatapidata_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='scrango.ChatAPIData')),
                ('api_key', models.CharField(max_length=255, verbose_name='API Token')),
                ('roomid', models.CharField(max_length=128, verbose_name='roomid')),
            ],
            bases=('scrango.chatapidata',),
        ),
        migrations.CreateModel(
            name='SlackAPIData',
            fields=[
                ('chatapidata_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='scrango.ChatAPIData')),
                ('webhook_url', models.CharField(max_length=1024, verbose_name='Webhook URL')),
                ('token', models.CharField(blank=True, max_length=512, null=True, verbose_name='Token(\u753b\u50cf\u9001\u4fe1API)')),
                ('channel_id', models.CharField(blank=True, max_length=255, null=True, verbose_name='ChannelID(\u753b\u50cf\u9001\u4fe1API)')),
            ],
            bases=('scrango.chatapidata',),
        ),
    ]
