# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import shared_task
from .models import CrawlerData, ScraperData, ResultData, ActionData
from django.conf import settings
from django.utils import timezone

import StringIO
from command_node_scraper import CommandNodeScraper, ScraperCommand
import urlparse
import json
import uuid
import os
import datetime

from slack_interface import SlackInterface
from chatwork_interface import ChatworkInterface
from template_system import TemplateSystem
from selenium_loader import SeleniumLoader, FormAction


# スラックインターフェイス
SLACK = SlackInterface(username="scrango")
CHATWORK = ChatworkInterface()
# スクリーンショット値抜き器
TEMPLATE_SYSTEM = TemplateSystem("($$px,$$px)")


@shared_task
def do_scrape(crawler_data):
    """ スクレイピングをする """
    try:
        # 状態変遷
        crawler_data.state = "executing" # 状態-> 実行中
        crawler_data.last_execute_time = timezone.now() # 最終実行時間-> 今
        crawler_data.save()

        # スクレイピングデータ取得
        url = crawler_data.url
        screenshot_size = crawler_data.screenshot # スクリーンショット取るか否か
        notification = crawler_data.notification # 通知先

        # クローラーからアクション抽出
        action_list = [
            FormAction( # アクションデータをフォームアクション化
                a.selector
                ,a.action_type
                ,a.content
            ) for a in ActionData.objects.filter(crawler=crawler_data) if a.valid # only valid
        ]

        # JSパーシング済みHTML取得
        with SeleniumLoader() as selen :
            # url読む
            selen.load_url(url)
            # アクション処理
            selen.apply_formActions(*action_list)
            # HTML抜く
            html = selen.get_source()

            # スクリーンショットとっちゃう
            if screenshot_size :
                # ファイル名作る
                _uuid = str(uuid.uuid4())[:10]
                media_path = settings.MEDIA_ROOT
                filename = os.path.join(media_path, _uuid +"_screenshot.png")
                # スクリーンショットサイズの解析
                x,y = TEMPLATE_SYSTEM.extract_from(screenshot_size)
                # とる
                selen.set_size(x,y).save_screenshot(filename)

            else :
                filename = None # ダミー

        # コマンドノードツリー生成
        root = gen_commandNodeTree(crawler_data)

        # スクレイピング
        scraper = CommandNodeScraper()
        scraper.parse(html)
        jsoned = scraper.call(root,"json")

        # 結果の保存
        # リザルトオブジェクト
        resultObj = ResultData(
            crawler = crawler_data,
            json = jsoned,
            result = "success",
            screenshot = filename
            ).save() # 保存

        # 状態変遷
        crawler_data.state = "active"
        crawler_data.save()

        # 通知
        notificate_it(notification,scraper,filename)

    except :
        # 状態変遷
        crawler_data.state = "error" # 状態-> エラー
        crawler_data.save()
        import traceback; traceback.print_exc()


def notificate_it(notification,scraper,filename):
    """ 通知する """
    if notification == "slack":
        # そのままJSONダンプ
        data = json.dumps(
            scraper.get_result(),
            ensure_ascii = False,
            indent = 4
            )
        SLACK.send_message(data,filename)

    elif notification == "chatwork":
        # そのままJSONダンプ
        data = json.dumps(
            scraper.get_result(),
            ensure_ascii = False,
            indent = 4
            )
        CHATWORK.send_message(data)


def gen_commandNodeTree(crawler_data):
    """ クローラーからコマンドノード生成す"""
    # コマンドノード作る 
    root = ScraperCommand("root",None)

    # クローラーに関連づいたすべてのスクレイパ情報からコマンドツリー作る
    tmp_dict = dict() # { scraper_data : commandNode }
    for scraper_data in ScraperData.objects.filter(crawler=crawler_data, valid=True) :
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
        master_scraper = ScraperData.objects.get(crawler=crawler_data, name=key).master_scraper

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
    #now = datetime.datetime.now()
    now = timezone.now()
    # 繰り返しフラグの立つている全クローラを検索
    for crawler_data in CrawlerData.objects.all() :
        if crawler_data.repetition :
            # 最終実行時間
            last_execute_time = crawler_data.last_execute_time # エラるのでTZ無視
            repetition = int(crawler_data.repetition) # 繰り返し間隔sec

            # 計算 : 最終実行時間が今からrepetition秒前の時間より前か
            if ( not last_execute_time ) or ( now -last_execute_time > datetime.timedelta(seconds=repetition) ):
                # クローリングする
                do_scrape.delay(crawler_data)
                print "do delay"



