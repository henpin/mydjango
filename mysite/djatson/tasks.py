# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import shared_task
from .models import CrawlerData, DjatsonLogData

import StringIO

from watson_api.scratson import Scratson


@shared_task
def initialize_watson(crawler_data):
    """
    watsonを初期化する
    # コンテキスト
    * CrawlerDataモデルインスタンス

    # steps 
    1. ワークスペースの初期化
        * WS_IDの関連付け
    2. カンバゼーション生成
        * 状態フラグの変更
    """
    log = [] # ログリスト
    log.append("Watson生成を開始しました")
    try :
        # 初期化中フラグ上げる
        crawler_data.state = 'crawling'
        crawler_data.save()

        log.append("初期化情報を取得中...")
        # 情報取得
        ws_id = crawler_data.ws_id
        name = crawler_data.name
        url = crawler_data.url
        #selector = crawler_data.selector # 廃止予定

        # watsonインターフェイス初期化
        watson = Scratson()

        log.append("ワークスペース初期化中...")
        # ワークスペース初期化
        generated = watson.initialize_workspace(ws_id,name)

        # ワークスペースIDないなら保存
        if not ws_id :
            crawler_data.ws_id = generated
            crawler_data.save()

        log.append("Webページクロール中...")
        # ファイル風オブジェクト(解析済みjson受け取り用)
        _file = StringIO.StringIO()
        # urlからスクレイピングしてwatson生成
        watson.main(url,_file)

        # モデル状態更新
        crawler_data.state = "active" # 終了フラグ上げる
        crawler_data.save()

        log.append("ログデータ収集中...")
        log.append("Watson生成が正常に完了しました...")
        # 取得済みJSONの保存
        DjatsonLogData(
            crawler = crawler_data,
            json = _file.getvalue(),      # 結果JSON
            result = "success",
            log = "\n".join(log),
            ).save() # 保存

    except Exception as e:
        import traceback; traceback.print_exc()
        log.append("エラーが発生しました")
        log.append(str(e))

        # とりあえずログとっとく
        DjatsonLogData(
            crawler = crawler_data,
            result = "failure",
            log = "\n".join(log),
            ).save() # 保存

        crawler_data.state = "error" # エラーフラグ
        crawler_data.save()


