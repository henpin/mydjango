# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import shared_task
from .models import CrawlerData, ScraperData, ResultData, ActionData
from .models import ChatAPIData, SlackAPIData, ChatworkAPIData
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
from image_utils import ImageUtil

import re_utils as reu

# スクリーンショット値抜き器
TEMPLATE_SYSTEM = TemplateSystem("($$px,$$px)")
# スクリーンショット類似度比較器
IMAGE_UTILS = ImageUtil()


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
        user_agent = crawler_data.user_agent # ユーザーエージェント

        # クローラーからアクション抽出
        action_list = [
            FormAction( # アクションデータをフォームアクション化
                a.selector
                ,a.action_type
                ,a.content
            ) for a in ActionData.objects.filter(crawler=crawler_data) if a.valid # only valid
        ]

        # JSパーシング済みHTML取得
        with SeleniumLoader(user_agent) as selen :
            # url読む
            selen.load_url(url)
            # アクション処理
            selen.apply_formActions(*action_list)
            # HTML抜く
            html = selen.get_source()

            # スクリーンショットとっちゃう
            if screenshot_size :
                # ファイル名作る
                _uuid = str(uuid.uuid4())
                media_path = settings.MEDIA_ROOT
                filename = os.path.join(media_path, _uuid +"_ss.png")
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
            json = jsoned,      # 結果JSON
            result = "success",
            screenshot = filename, # スクリーンショットURL
            ).save() # 保存

        # 状態変遷
        crawler_data.state = "active"
        crawler_data.save()

        # 通知
        notificate_it(
            crawler_data,
            scraper.get_result(),
            filename,
            )

        return jsoned

    except Exception as e:
        import traceback; traceback.print_exc()
        # 結果JSON作成
        result_data = {
            "error_message" : reu.decode(str(e)) # エラーメッセージ
        }

        # 結果の保存
        resultObj = ResultData(
            crawler = crawler_data,
            json = json.dumps(result_data),
            result = "failure",
            ).save() # 保存

        # 状態変遷
        crawler_data.state = "error" # 状態-> エラー
        crawler_data.save()

        # 通知
        notificate_it(crawler_data, result_data, error=True) # 失敗なら強制通知

        return json.dumps(result_data)


def notificate_it(crawler_data,result_data,filename="",error=False):
    """ 通知する"""
    # 通知周りの情報を抜く
    notification = crawler_data.notification.convert2entity() # 通知先 : 具象クラスに落とす
    notification_cond = crawler_data.notification_cond # 通知条件

    # 通知できるか判定
    if not notification :
        return  # さよなら
   
    # 通知条件判定
    if error :
        pass
    elif notification_cond == "always" :
        pass
    elif notification_cond == "changed":
        # 最終取得結果抜く
        results = ResultData.objects.filter(crawler=crawler_data).order_by('-datetime')
        if len(results) >=2:
            last_result = results[1] # 1こ前
            last_result_dic = json.loads(last_result.json or "") # 辞書に復元
            # 結果比較
            if result_data == last_result_dic :
                return # 一緒なら通知しない
    elif notification_cond in ("ss_changed","ss_changed2"):
        # 最終取得結果からss抜く
        results = ResultData.objects.filter(crawler=crawler_data).order_by('-datetime')
        if len(results) >= 2:
            last_result = results[1] # 1こ前
            last_result_ss = str(last_result.screenshot)
            # 結果比較
            if not filename:
                msg = "通知条件エラー通知条件にスクリーンショット比較が定義されていますが、スクリーンショット取得設定がされていません"
                raise Exception(msg) # 比較不能

            if last_result_ss :
                similarity = IMAGE_UTILS.calc_similarity(last_result_ss,filename)
                print similarity
                if notification_cond == "ss_changed" and similarity == 1:
                    return # 完全一致なら通知しない
                elif notification_cond == "ss_changed2" and similarity > 0.5:
                    return # 閾値委譲なら通知しない

    # メッセージ作成
    message = create_notification_message(result_data)

    # slack通知処理
    if isinstance(notification,SlackAPIData):
        # データ抜く
        user_name = notification.user_name
        webhook_url = notification.webhook_url
        token = notification.token
        channel_id = notification.channel_id

        # スラックインターフェイス起こす
        slack = SlackInterface(username=(user_name or "scrango"))
        # データの注入
        slack.injects(
            url = webhook_url,
            file_upload_token = token,
            channel_id = channel_id
        )
        # 通知 
        slack.send_message(message,filename)

    # chatwork通知処理
    elif isinstance(notification,ChatworkAPIData):
        # データ抜く
        user_name = notification.user_name
        api_key = notification.api_key
        roomid = notification.roomid

        # インターフェイス起こす
        chatwork = ChatworkInterface()
        # データ注入
        chatwork.injects(
            apikey = api_key,
            roomid = roomid
        )
        # 通知
        chatwork.send_message(message)


def create_notification_message(result_data):
    """ 抽出済みJSON元データから、通知に耐えうるデータに変換する"""
    # 再帰ジェネレータでｶﾞﾝｶﾞﾝやってyieldする
    return u"\n".join(item2message(result_data))


def item2message(item,prefix="",indent=0):
    """ 
    オブジェクトをメッセージ化する
    再帰ジェネレータモデル
    """
    indentate = lambda _str : (u"  " *indent) +_str

    if isinstance(item,dict):
        for key,val in item.items() :
            if isinstance(val,(str,unicode)) and val :
                _str = u"%s : 「%s」" % (key,val)
                yield indentate(_str)

            elif isinstance(val,list):
                for i,_ in enumerate(val) :
                    _prefix = u"%s(%d)" % (key,i+1)
                    for v in item2message(_,_prefix,indent+1):
                        yield v
                yield "" # 空白おく

        yield "" # 空白おく

    elif isinstance(item,(unicode,str)) and item:
        yield indentate(u"%s : 「%s」" % (prefix,item))



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
            result = []
            # くるくるする
            for _tag in tag :
                # 情報抽出
                if target == "html" :
                    result.append( unicode(_tag) )
                elif target == "text" :
                    result.append( _tag.get_text().strip() )
                elif target == "src":
                    result.append( _tag["src"] )
                elif target == "href":
                    href = _tag["href"]
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
                        print "HREF Done"
                        return result

                    result.append( _tag["href"] )

            # 返す
            return result

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



