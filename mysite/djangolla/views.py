# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os, json, uuid

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from .models import FormData, InputData, LogManageData, LogData

# JS template file
TEMPLATE_JS_PATH = os.path.dirname(os.path.abspath(__file__)) + '/static/template.js'
TEMPLATE_REPLAYJS_PATH = os.path.dirname(os.path.abspath(__file__)) + '/static/replay_template.js'

# general
def generate_validation_json(inputs):
    """ inputデータのリストから、バリデーション情報JSONを生成 """
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

    return jsoned



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

    # JSON化
    jsoned = generate_validation_json(inputs)

    # JS生成
    with open(TEMPLATE_JS_PATH) as f :
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
        _uuid = req.POST["uuid"] # UUID

        # ログオブジェクト
        logObj = LogData(
            input_name=input_name, 
            input_value=input_value,
            manager = get_object_or_404(LogManageData,uuid=_uuid), # UUID
            )

        # 保存
        logObj.save()

        return HttpResponse("OK")


class ReplayView(generic.TemplateView):
    """ リプレイHTMLを描画 """
    template_name = "djangolla/result.html"

    def get_context_data(self, **kwargs):
        # コンテキスト取得
        context = super(ReplayView, self).get_context_data(**kwargs)
        # データ取得
        _uuid = kwargs["uuid"]
        logm = get_object_or_404(LogManageData,uuid=_uuid) # ログマネージャ取得
        form = logm.form # フォームオブジェクト
        # 束縛
        context['object_list'] = InputData.objects.filter(parent_form=form) # フォームからinput生成
        context["form_name"] = form.form_name
        context["uuid"] = _uuid
        # リプレイフラグ上げる
        context["replay_flg"] = True

        return context

def get_replay_js(req, _uuid):
    """ リプレイ用JS生成する"""
    # UUIDからログマネージャとフォームとログデータ取得
    logm = get_object_or_404(LogManageData,uuid=_uuid) # ログマネージャ取得
    log_data = LogData.objects.filter(manager=logm).order_by("datetime") # ログマネージャからログとり
    _form = logm.form
    form_name = _form.form_name

    # バリデーション情報つくってJSON化
    inputs = InputData.objects.filter(parent_form=_form) # formから取得されるinput情報リスト
    validation_data_json = generate_validation_json(inputs) # JSON化

    # リプレイデータJSONデータ作る
    if log_data:
        data_list = list() # 正規化されたログデータリスト

        # 最初の要素を取得
        first_log = log_data[0]
        data = {
            "time" : 0, # 起点
            "input_name" : first_log.input_name,
            "input_value" : first_log.input_value
            } # 辞書化
        data_list.append(data) # 登録

        # ぐるぐるして辞書化
        for log in log_data[1:] :
            data = {
                "time" : (log.datetime -first_log.datetime).seconds, # 差分時間(秒)
                "input_name" : log.input_name,
                "input_value" : log.input_value
            }
            data_list.append(data) # 保存

        # ログ情報JSON化
        log_data_json = json.dumps(data_list)

    else :
        log_data_json = str("[]")


    # JS生成
    with open(TEMPLATE_REPLAYJS_PATH) as f :
        # リプレイ用テンプレ読み込む
        js_template = f.read()

    # テンプレートにJSON注入
    js_template = js_template.replace(str("{{ RULES_OBJ }}"), validation_data_json)
    js_template = js_template.replace(str("{{ FORM_NAME }}"), form_name.encode("utf-8")) # フォーム名
    js_template = js_template.replace(str("{{ REPLAY_DATA }}"), log_data_json)

    return HttpResponse(js_template, content_type="text/javascript; charset=UTF-8")

