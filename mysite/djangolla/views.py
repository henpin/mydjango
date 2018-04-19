# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from .models import FormData, InputData

# Create your views here.
class ResultView(generic.DetailView):
    model = FormData
    context_object_name = 'formData'
    template_name = "djangolla/result.html"
    slug_url_kwarg = "form_name"  # コンテキスト受け取り名
    slug_field = "form_name"  # クエリフィールド


def get_js(req, form_name):
    """ とりまJS生成する"""
    # form_nameで取得されるinput情報リスト
    #_form = FormData.objects.get(form_name=form_name)
    _form = get_object_or_404(FormData, form_name=form_name)
    inputs = InputData.objects.filter(parent_form=_form)

    # 挿入文字列
    text = "\\n".join( "インプット名 : %s, インプットタイプ : %s" % (_input.input_name, _input.input_type)
        for _input in inputs.all() )

    src = """
    window.onload = function(){
        alert("JS取得!!!"); 
        alert("取得内容:\\n%s")
        }
    """ % (text,)
    return HttpResponse(src, content_type="text/javascript; charset=UTF-8")

