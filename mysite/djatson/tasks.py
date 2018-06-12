# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import shared_task
from .models import CrawlerData, DjatsonLogData, CrawlingLogData, HtmlData

import StringIO

from general_crawler.raw_html_crawler import RawHTMLSpider, RawHTMLCrawler
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

        # 情報取得
        log.append("初期化情報を取得中...")
        ws_id = crawler_data.ws_id
        name = crawler_data.name
        url = crawler_data.url

        # watsonインターフェイス初期化
        watson = Scratson()

        # ワークスペース初期化
        log.append("ワークスペース初期化中...")
        generated = watson.initialize_workspace(ws_id,name)

        # ワークスペースIDないなら保存
        if not ws_id :
            crawler_data.ws_id = generated
            crawler_data.save()

        # ファイル風オブジェクト(解析済みjson受け取り用)
        log.append("Webページクロール中...")
        _file = StringIO.StringIO()
        # urlからスクレイピングしてwatson生成
        watson.main(url,_file)

        # モデル状態更新
        crawler_data.state = "active" # 終了フラグ上げる
        crawler_data.save()

        # 取得済みJSONの保存
        log.append("ログデータ収集中...")
        log.append("Watson生成が正常に完了しました...")
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



@shared_task
def do_crawl(crawler_data):
    """ クローリングする """
    # ログデータに関連付けてHTML保存するので名前取っておきたい
    logdata = None

    log = [] # ログリスト
    log.append("Watson生成を開始しました")
    try :
        # 初期化中フラグ上げる
        crawler_data.state = 'crawling'
        crawler_data.save()

        # 情報取得
        log.append("初期化情報を取得中...")
        ws_id = crawler_data.ws_id
        name = crawler_data.name
        url = crawler_data.url

        # クローラー初期化
        log.append("クローラーを構築中...")
        RawHTMLSpider.start_urls = [ url ]
        crawler = RawHTMLCrawler()
        
        # クローリング
        log.append("Webページクロール中...")
        crawler.do_crawl()

        # ログデータ作る
        log.append("クロール終了中...")
        logdata = CrawlingLogData(
            crawler = crawler_data,
            result = "success",
        )
        logdata.save() # 保存

        # データ集計
        log.append("データを集計中...")
        for key,val in crawler.get_data().items() :
            # HTMLデータの保存
            HtmlData(     
                crawlinglog = logdata,
                url = key,
                html = val[0]
            ).save()

        # ログデータ保存
        log.append("クロールが正常に完了しました...")
        logdata.log = "\n".join(log)
        logdata.save()

        # モデル状態更新
        crawler_data.state = "active" # 終了フラグ上げる
        crawler_data.save()


    except Exception as e:
        import traceback; traceback.print_exc()
        log.append("エラーが発生しました")
        log.append(str(e))

        # ログとる
        if logdata :
            logdata.result = "failure"
            logdata.log = "\n".join(log)
            logdata.save() # 上書き

        else :
            # ログデータ作る
            CrawlingLogData(
                log = "\n".join(log),
                crawler = crawler_data,
                result = "success",
            ).save() # 保存

        crawler_data.state = "error" # エラーフラグ
        crawler_data.save()


