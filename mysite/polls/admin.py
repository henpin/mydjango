# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Question, Choice

def update_q(model_admin, req, querySet):
    """ """
    print "DONE!!!"


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    filedsets = [
        ("pub_date", { "fields" : ["question_text"] } ),
        ("Date", {"fields" : ["pub_date"], "classes" : ["collapse"]})
    ]
    inlines = [ChoiceInline]
    list_display = ("question_text", "pub_date")
    actions = [update_q]
    
    def save_model(self, request, obj, form, change):
        # とりまスーパー
        super(QuestionAdmin, self).save_model(request, obj, form, change)
        print "GOOOD"

# Register your models here.
#admin.site.register(Question, QuestionAdmin)
#admin.site.register(Choice)

# ヘッダ編集
admin.AdminSite.site_header = u"pollsデモサイト"
