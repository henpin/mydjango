# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import shared_task
from .models import CrawlerData, ScraperData, ResultData

import StringIO
from command_node_scraper import CommandNodeScraper, ScraperCommand

@shared_task
def do_scrape(crawler_data):
    """ スクレイピングをする """
    # スクレイピングデータ取得
    url = crawler_data.url
    
    # コマンドノード作る 
    root = ScraperCommand("root",None)

    # クローラーに関連づいたすべてのスクレイパ情報からコマンドツリー作る
    tmp_dict = dict() # { scraper_data : commandNode }
    for scraper_data in ScraperData.objects.filter(crawler=crawler_data) :
        # 情報取得
        name = scraper_data.name
        selector = scraper_data.selector
        target = scraper_data.target
        #master_scraper = scraper_data.master_scraper

        # コマンド組み立て
        command = gen_command(target)
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

    # スクレイピング
    scraper = CommandNodeScraper()
    scraper.parse_fromURL(url)
    json = scraper.call(root,"json")

    # 結果の保存
    # リザルトオブジェクト
    resultObj = ResultData(
        crawler = crawler_data,
        json = json,
        result = "success"
        )

    # 保存
    resultObj.save()


def gen_command(target):
    """ コマンド作り出す"""
    def command(tag):
        try:
            if target == "html" :
                pass
            elif target == "text" :
                return tag[0].get_text()
            elif target == "src":
                return tag[0]["src"]
            elif target == "href":
                return tag[0]["href"]

        except :
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

