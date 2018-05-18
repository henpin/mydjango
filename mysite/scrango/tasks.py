# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import shared_task
from .models import CrawlerData, ScraperData, ResultData

import StringIO
from command_node_scraper import CommandNodeScraper, ScraperCommand
import urlparse
import json

from slack_interface import SlackInterface

# スラックインターフェイス
SLACK = SlackInterface(username="scrango")


@shared_task
def do_scrape(crawler_data,notification=None):
    """ スクレイピングをする """
    # スクレイピングデータ取得
    url = crawler_data.url

    # コマンドノードツリー生成
    root = gen_commandNodeTree(crawler_data)

    # スクレイピング
    scraper = CommandNodeScraper()
    scraper.parse_fromURL(url)
    jsoned = scraper.call(root,"json")

    # 結果の保存
    # リザルトオブジェクト
    resultObj = ResultData(
        crawler = crawler_data,
        json = jsoned,
        result = "success"
        )

    # 保存
    resultObj.save()

    # 状態変遷
    crawler_data.state = "active"
    crawler_data.save()

    # 通知
    if notification == "slack":
        # そのままJSONダンプ
        data = json.dumps(
            scraper.get_result(),
            ensure_ascii = False,
            indent = 4
            )
        SLACK.send_message(data)


def gen_commandNodeTree(crawler_data):
    """ クローラーからコマンドノード生成す"""
    # コマンドノード作る 
    root = ScraperCommand("root",None)

    # クローラーに関連づいたすべてのスクレイパ情報からコマンドツリー作る
    tmp_dict = dict() # { scraper_data : commandNode }
    for scraper_data in ScraperData.objects.filter(crawler=crawler_data) :
        # 情報取得
        name = scraper_data.name
        selector = scraper_data.selector
        target = scraper_data.target
        # 再帰クローラー検索
        r_crawler_name = scraper_data.crawler_name
        if r_crawler_name :
            r_crawler = CrawlerData.objects.get(name=r_crawler_name) 
        else :
            r_crawler = None
        #master_scraper = scraper_data.master_scraper

        # コマンド組み立て
        command = gen_command(target,r_crawler,crawler_data.url)
        # フィルタラ組み立て
        filterer = gen_filterer(selector)

        # コマンド起こして一時保管
        tmp_dict[name] = ScraperCommand(name,command,filterer)
        
    # 関連付け
    for key,val in tmp_dict.items():
        # 親読む
        master_scraper = ScraperData.objects.get(name=key).master_scraper

        # マスターがあればそこにつける
        if master_scraper :
            tmp_dict[master_scraper.name].add_child(val)

        # マスターが無ければルートにつける
        else :
            root.add_child(val)

    return root


def gen_command(target, crawler=None, url_prefix=""):
    """ コマンド作り出す"""
    def command(tag):
        try:
            # 情報抽出
            if target == "html" :
                pass
            elif target == "text" :
                return tag[0].get_text()
            elif target == "src":
                return tag[0]["src"]
            elif target == "href":
                href = tag[0]["href"]
                # 再帰クローラーがあれば再帰処理
                if crawler and href :
                    # 絶対パス化
                    href_abs = urlparse.urljoin(url_prefix, href)
                    print href_abs
                    # ノードツリー生成
                    root = gen_commandNodeTree(crawler)
                    # スクレイパ生成
                    scraper = CommandNodeScraper()
                    scraper.parse_fromURL(href_abs)
                    # スクレイピング
                    result = scraper.call(root)
                    print "Done"
                    return result

                return tag[0]["href"]

        except IndexError, KeyError:
            pass # もみ消し

    return command


def gen_filterer(selector):
    """ フィルタラ作り出す"""
    def filterer(tag):
        try:
            # セレクトする
            return tag.select(selector)

        except :
            return tag # もみ消し

    return filterer


@shared_task
def apply_shcedule():
    """ スケジューリング処理 """
    # 全クローラを抜いて処理
    for crawler_data in CrawlerData.objects.all() :
        if crawler_data.repetition :
            # クローリングする
            do_scrape.delay(crawler_data,notification="slack")
            print "do delay"


