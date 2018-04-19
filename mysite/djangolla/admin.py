# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import FormData, InputData

class InputDataInline(admin.TabularInline):
    """ Input入力欄を並べるやつ """
    model = InputData
    extra = 3


class FormDataAdmin(admin.ModelAdmin):
    """ フォームデータ編集Admin """
    # 並べる
    inlines = [InputDataInline]
    #list_display = ("form_name")
    
# Register your models here.
admin.site.register(FormData, FormDataAdmin)

# ヘッダ編集
admin.AdminSite.site_header = u"Djangollaデモサイト"
