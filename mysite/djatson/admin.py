# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# general
from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse
# modules
from .apps import gen_url

# Models
from .models import URLData

# extenstions
from django_admin_row_actions import AdminRowActionsMixin



# Register your models here.
class URLDataAdmin(AdminRowActionsMixin, admin.ModelAdmin):
    """ URLデータのアド民 """
    # アクション
    actions = [
    ]
    # 並べる
    list_display = ("url","name","state","ws_id","description")

    def get_row_actions(self, item):
        """ プラグイン用行アクション """
        # url生成
        url_for_json = gen_url("json",item.name)
        url_for_chat = gen_url("chat",item.name)
        url_for_initialize = gen_url("initialize",item.name)
        row_actions = [
            {
                'label': '解析結果を表示',
                'url' : url_for_json
            },
            {
                'label': 'watsonを初期化',
                'url' : url_for_initialize
            },
            {
                'label': 'watsonとしゃべる',
                'url' : url_for_chat
            }
        ]

        return row_actions




# Global admin settings
admin.site.register(URLData, URLDataAdmin)
