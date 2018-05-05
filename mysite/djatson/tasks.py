# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import shared_task
from .models import URLData

from watson_api.scratson import Scratson


@shared_task
def initialize_watson(url_data):
    """
    watsonを初期化する
    # コンテキスト
    * URLDataのモデルインスタンス

    # steps 
    1. ワークスペースの初期化
        * WS_IDの関連付け
    2. カンバゼーション生成
        * 状態フラグの変更
    """
    try :
        # 初期化中フラグ上げる
        url_data.state = 'initializing'
        url_data.save()

        # 情報取得
        ws_id = url_data.ws_id
        name = url_data.name
        url = url_data.url

        # watsonインターフェイス初期化
        watson = Scratson()

        # ワークスペース初期化
        generated = watson.initialize_workspace(ws_id,name)

        # ワークスペースIDないなら保存
        if not ws_id :
            url_data.ws_id = generated
            url_data.save()

        # urlからスクレイピングしてwatson生成
        watson.main(url)

        # 終了フラグ上げる
        url_data.state = "active"
        url_data.save()

    except Exception as e:
        print e
        url_data.state = "error" # エラーフラグ
        url_data.save()

