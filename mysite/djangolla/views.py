# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os, json, uuid, datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from .models import FormData, InputData, LogManageData, LogData

# JS template file
TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/static/template.js'

# Create your views here.
class ResultView(generic.TemplateView):
    """ デモHTMLを描画 """
    template_name = "djangolla/result.html"

    def get_context_data(self, **kwargs):
        # コンテキスト取得
        context = super(ResultView, self).get_context_data(**kwargs)
        # データ取得
        form_name = kwargs["form_name"]
        context['object_list'] = InputData.objects.filter(parent_form__form_name=form_name)
        # 識別用UUID
        _uuid = str(uuid.uuid4())
        context["uuid"] = _uuid
        # ログマネージャに置いとく
        form = get_object_or_404(FormData,form_name=form_name)
        LogManageData(uuid=_uuid, form=form).save()

        return context


def get_js(req, form_name):
    """ とりまJS生成する"""
    # form_nameで取得されるinput情報リスト
    _form = get_object_or_404(FormData, form_name=form_name)
    inputs = InputData.objects.filter(parent_form=_form)

    # バリデーション情報辞書作る
    validation_info_dic = dict()
    for data in inputs.all() :
        # また辞書つくる
        info_dic = dict()

        # 情報投入
        info_dic[data.input_type] = True # インプットタイプ
        info_dic["required"] = [data.require, data.input_name] # 必須

        # 登録
        validation_info_dic[data.input_name] = info_dic

    # JSON化
    jsoned = json.dumps(validation_info_dic) # JSOn化

    # JS生成
    with open(TEMPLATE_DIR) as f :
        # テンプレ読み込む
        js_template = f.read()

    # テンプレートにJSON注入
    js_template = js_template.replace(str("{{ RULES_OBJ }}"), jsoned)
    js_template = js_template.replace(str("{{ FORM_NAME }}"), form_name.encode("utf-8")) # フォーム名

    return HttpResponse(js_template, content_type="text/javascript; charset=UTF-8")


def log_it(req):
    """ Ajaxロギングする """
    # POSTだけ処理
    if req.method == 'POST':
        # ログオブジェクト作る
        input_name = req.POST['input_name'] # input名
        input_value = req.POST["input_value"] # input値
        uuid = req.POST["uuid"] # UUID

        # ログオブジェクト
        logObj = LogData(
            input_name=input_name, 
            input_value=input_value,
            uuid = get_object_or_404(LogManageData,uuid=uuid), # UUID
            datetime = datetime.datetime.now(),
            )

        # 保存
        logObj.save()

        return HttpResponse("OK")


class ReplayView(generic.TemplateView):
    """ リプレイHTMLを描画 """
    template_name = "djangolla/result.html"

    def get_context_data(self, **kwargs):
        # コンテキスト取得
        context = super(ResultView, self).get_context_data(**kwargs)
        # データ取得
        _uuid = kwargs["uuid"]
        context['object_list'] = LogData.objects.filter(manager__uuid=_uuid)

        # リプレイデータ生成

        # リプレイデータ埋め込み

        return context


