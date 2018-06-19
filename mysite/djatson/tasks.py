# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import shared_task
from .models import CrawlerData, DjatsonLogData, CrawlingLogData, HtmlData

import StringIO
import requests

from general_crawler.raw_html_crawler import RawHTMLSpider, RawHTMLCrawler
from general_crawler.spynder import Spynder, SpynderTarget
from general_crawler.keyword_crawler import KeywordCrawler, KeywordSpider
from watson_api.scratson import Scratson
from gcp_interface import GCPInterface


# Globals
GCP_INTERFACE = GCPInterface()


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
        crawler_data.refresh_from_db()
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
            log.append("ワークスペースを新たに生成しました")
            crawler_data.refresh_from_db()
            crawler_data.ws_id = generated
            crawler_data.save()

        # ファイル風オブジェクト(解析済みjson受け取り用)
        log.append("Webページクロール中...")
        _file = StringIO.StringIO()
        # urlからスクレイピングしてwatson生成
        watson.main(url,_file)

        # モデル状態更新
        crawler_data.refresh_from_db()
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

        crawler_data.refresh_from_db()
        crawler_data.state = "error" # エラーフラグ
        crawler_data.save()


@shared_task
def initialize_watson_fromCrawledData(crawler_data):
    """ クロールログからwatsonの初期化 """
    log = [] # ログリスト
    log.append("Watson生成を開始しました")
    try :
        # 初期化中フラグ上げる
        crawler_data.refresh_from_db()
        crawler_data.state = 'crawling'
        crawler_data.save()

        # 情報取得
        log.append("初期化情報を取得中...")
        ws_id = crawler_data.ws_id
        name = crawler_data.name
        log_data = CrawlingLogData.objects.filter(crawler=crawler_data).latest("datetime") # 最新のログ

        # watsonインターフェイス初期化
        watson = Scratson()

        # ワークスペース初期化
        log.append("ワークスペース初期化中...")
        generated = watson.initialize_workspace(ws_id,name)

        # ワークスペースIDないなら保存
        if not ws_id :
            log.append("ワークスペースを新たに生成しました")
            crawler_data.refresh_from_db()
            crawler_data.ws_id = generated
            crawler_data.save()

        # JSON情報の構築
        log.append("Watsonデータの構築中...")
        # ログから全HTMLデータを抜き、そこからWatson生成用JSONを作り上げる
        targets = [] # スパインダーターゲッツ
        for html_data in HtmlData.objects.filter(crawlinglog=log_data):
            targets.append( SpynderTarget(html_data.url, html_data.html) )

        spynder = Spynder(KeywordSpider) # キーワードスパイダベースで起こす
        spynder.do_parse(*targets) # パースする : JSON構築

        # JSONからWatson生成
        log.append("Watsonの生成中...")
        watson.main_fromSpider(spynder.spider) # スパイダを直接渡す

        # 取得済みJSONの保存
        log.append("ログデータ収集中...")
        log.append("Watson生成が正常に完了しました...")
        DjatsonLogData(
            crawler = crawler_data,
            json = spider.get_additional_data(), # 結果JSON
            result = "success",
            log = "\n".join(log),
            ).save() # 保存

        # モデル状態更新
        crawler_data.refresh_from_db()
        crawler_data.state = "active" # 終了フラグ上げる
        crawler_data.save()

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

        crawler_data.refresh_from_db()
        crawler_data.state = "error" # エラーフラグ
        crawler_data.save()


@shared_task
def do_crawl(crawler_data):
    """ クローリングする """
    # ログデータに関連付けてHTML保存するので名前取っておきたい
    logdata = None

    log = [] # ログリスト
    log.append("クローリングを開始しました")
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


@shared_task
def do_keywordCrawl(crawler_data):
    """ キーワードベースのクローリングする """
    # ログデータに関連付けてHTML保存するので名前取っておきたい
    logdata = None

    log = [] # ログリスト
    log.append("クローリングを開始しました")
    try :
        # 初期化中フラグ上げる
        crawler_data.refresh_from_db()
        crawler_data.state = 'crawling'
        crawler_data.save()

        # データ抜く
        keyword = crawler_data.keyword
        if not keyword:
            raise NameError("キーワードが定義されていません")

        # まずはGCPインターフェイスからURL検索かける
        result = GCP_INTERFACE.search_query(keyword)

        # クローリングしてresultに詰め込んでおく
        for r in result :
            try :
                url = r["url"]
                res = requests.get(url) # GETする
                res.encoding = res.apparent_encoding  # なんかエンコーディング処理
                r["html"] = res.text # そのままbody部を格納

            except requests.exceptions.SSLError as e:
                # たまにSSL証明書エラーがでるのでそのときはあきらめる
                r["html"] = ""
            
        # 先にログデータ作る
        log.append("クロール終了中...")
        logdata = CrawlingLogData(
            crawler = crawler_data,
            result = "success",
        )
        logdata.save() # 保存

        # データ集計
        log.append("データを集計中...")
        for data in result :
            # HTMLデータの保存
            HtmlData(     
                crawlinglog = logdata,
                url = data["url"],
                html = data["html"], 
                title = data["title"]
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


