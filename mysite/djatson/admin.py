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
    list_display = ("url","name","initialized","ws_id")

    def get_row_actions(self, item):
        """ プラグイン用行アクション """
        # url生成
        url = gen_url("chat",item.name)
        row_actions = [
            {
                'label': 'watsonとしゃべる',
                'url' : url
            }
        ]

        return row_actions




# Global admin settings
admin.site.register(URLData, URLDataAdmin)
