# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import shared_task
from .models import ScraperData, ScraperInfoData, ResultData, ActionData
from .models import ChatAPIData, SlackAPIData, ChatworkAPIData, LineAPIData, TwitterAPIData
from .models import WebAPIData, WebAPIResultData, WebAPIParameterData, WebAPIHttpHeaderParameterData
from django.conf import settings
from django.utils import timezone

from command_node_scraper import CommandNodeScraper, ScraperCommand
import StringIO
import urlparse
import json
import uuid
import os
import datetime
import itertools
import time, random

from slack_interface import SlackInterface
from chatwork_interface import ChatworkInterface
from twitter_interface import TwitterInterface
from line_interface import LineInterface
from template_system import TemplateSystem
from selenium_loader import SeleniumLoader, FormAction
from image_utils import ImageUtil
from exception_utils import WebAPIException
import re_utils as reu
import requests

# スクリーンショット値抜き器
TEMPLATE_SYSTEM = TemplateSystem("($$px,$$px)")
# スクリーンショット類似度比較器
IMAGE_UTILS = ImageUtil()


@shared_task
def do_scrape(scraper_data,_url=None,_html=None):
    """ スクレイピングをする """
    log = [] # ログリスト
    log.append("スクレイピングを開始しました")
    try:
        # 状態変遷
        scraper_data.refresh_from_db()
        scraper_data.state = "executing" # 状態-> 実行中
        scraper_data.last_execute_time = timezone.now() # 最終実行時間-> 今
        scraper_data.save()

        log.append("スクレイピング情報を取得中...")
        # スクレイピングデータ取得
        scraper_data.refresh_from_db()
        url = _url or scraper_data.url # API用URL注入フック
        screenshot_size = scraper_data.screenshot # スクリーンショット取るか否か
        user_agent = scraper_data.user_agent # ユーザーエージェント
        selenium_mode = scraper_data.selenium_mode

        log.append("スクレイパーを初期化中...")
        # クローラーからアクション抽出
        action_list = [
            FormAction( # アクションデータをフォームアクション化
                a.selector
                ,a.action_type
                ,a.content
            ) for a in ActionData.objects.filter(scraper=scraper_data) if a.valid # only valid
        ]

        # Seleniumモード : JSパーシング済みHTML取得
        log.append("Webページ取得中...")
        filename = None # ダミー
        html = "" # ダミー

        if _html :
            # HTMLの外部注入
            html = _html

        else :
            # HTML取得
            if selenium_mode :
                with SeleniumLoader(user_agent) as selen :
                    # url読む
                    selen.load_url(url)
                    log.append("フォーム操作実行中...")
                    # アクション処理
                    selen.apply_formActions(*action_list)
                    # HTML抜く
                    html = selen.get_source()

                    # スクリーンショットとっちゃう
                    if screenshot_size :
                        log.append("スクリーンショット取得中...")
                        # ファイル名作る
                        _uuid = str(uuid.uuid4())
                        media_path = settings.MEDIA_ROOT
                        filename = os.path.join(media_path, _uuid +"_ss.png")
                        # スクリーンショットサイズの解析
                        x,y = TEMPLATE_SYSTEM.extract_from(screenshot_size)
                        # とる
                        selen.set_size(x,y).save_screenshot(filename)
            else :
                time.sleep(1+random.random()*2) # ちょっと待つ : 再帰呼び出し対策
                # Seleniumモードで無いのならrequestsでシンプルにとる
                res = requests.get(url) # GETする
                res.encoding = res.apparent_encoding  # なんかエンコーディング処理
                html = res.text # body部取得

        # コマンドノードツリー生成
        log.append("セレクタ情報を構築中...")
        root = gen_commandNodeTree(scraper_data)

        # スクレイピング
        log.append("情報抽出中...")
        scraper = CommandNodeScraper()
        scraper.parse(html)
        jsoned = scraper.call(root,"json")

        # 結果の保存
        # 通知
        log.append("通知連携処理中...")
        notificate_it(
            scraper_data,
            scraper.get_result(),
            filename,
            )

        # リザルトオブジェクト
        log.append("スクレイピングが完了しました")
        ResultData(
            scraper = scraper_data,
            result_data = jsoned,      # 結果JSON
            result = "success",
            screenshot = filename, # スクリーンショットURL
            log = "\n".join(log) # ログデータ保存
            ).save() # 保存

        # 状態変遷
        scraper_data.refresh_from_db()
        scraper_data.state = "active"
        scraper_data.save()

        #return jsoned
        return scraper.get_result()

    except Exception as e:
        import traceback; traceback.print_exc()
        log.append("エラーが発生しました")
        log.append(str(e))
        # 結果JSON作成
        result_data = {
            "error_message" : reu.decode(str(e)) # エラーメッセージ
        }

        # 通知
        log.append("通知連携処理中...")
        notificate_it(scraper_data, result_data, error=True) # 失敗なら強制通知

        # 結果の保存
        log.append("スクレイピングが完了しました")
        ResultData(
            scraper = scraper_data,
            result_data = json.dumps(result_data),
            result = "failure",
            log = "\n".join(log) # ログデータ保存
            ).save() # 保存

        # 状態変遷
        scraper_data.refresh_from_db()
        scraper_data.state = "error" # 状態-> エラー
        scraper_data.save()

        #return json.dumps(result_datae)
        return result_data


def notificate_it(scraper_data,result_data,filename="",error=False):
    """ 通知する"""
    # 通知周りの情報を抜く
    notification = scraper_data.notification.convert2entity() if scraper_data.notification else None # 通知先 : 具象クラスに落とす
    notification_cond = scraper_data.notification_cond # 通知条件

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
        results = ResultData.objects.filter(scraper=scraper_data).order_by('-datetime')
        if len(results) >=2:
            last_result = results[1] # 1こ前
            last_result_dic = json.loads(last_result.result_data or "") # 辞書に復元
            # 結果比較
            if result_data == last_result_dic :
                return # 一緒なら通知しない
    elif notification_cond in ("ss_changed","ss_changed2"):
        # 最終取得結果からss抜く
        results = ResultData.objects.filter(scraper=scraper_data).order_by('-datetime')
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
    message = create_notification_message(scraper_data.name, result_data)
    # 送信
    send_notification(notification,message,filename)


@shared_task
def send_notification(notification,message,filename=""):
    """ 通知APIをつかって通知 """
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

    # Twitter通知
    elif isinstance(notification,TwitterAPIData):
        # データ抜く
        consumer_key = notification.consumer_key
        consumer_secret = notification.consumer_secret
        access_token = notification.access_token
        access_token_secret = notification.access_token_secret

        # インターフェイス起こす
        twitter = TwitterInterface()
        # データ注入
        twitter.injects(
            consumer_key = consumer_key,
            consumer_secret = consumer_secret,
            access_token = access_token,
            access_token_secret = access_token_secret
        )
        # 通知
        twitter.auth()
        twitter.send_tweet(message,filename)

    # Line通知
    elif isinstance(notification,LineAPIData):
        # データ抜く
        access_token = notification.access_token

        # インターフェイス起こす
        line = LineInterface()
        # データ注入
        line.injects(
            access_token = access_token
        )
        # 通知
        line.send_message(message,filename)




def create_notification_message(scraper_name,result_data):
    """ 抽出済みJSON元データから、通知に耐えうるデータに変換する"""
    # 再帰ジェネレータでｶﾞﾝｶﾞﾝやってyieldする
    return (u"スクレイピング「%s」を実行しました。\n\n" % (scraper_name)) +u"\n".join(item2message(result_data))



def item2message(item,prefix="",indent=-1):
    """ 
    オブジェクトをメッセージ化する
    再帰ジェネレータモデル
    """
    indentate = lambda _str : (u"  " *indent) +_str

    if isinstance(item,dict):
        for key,val in item.items() :
            if isinstance(val,(str,unicode)) and val :
                _str = u"【%s】%s" % (key,val)
                yield indentate(_str)

            elif isinstance(val,list):
                for i,_ in enumerate(val) :
                    _prefix = u"%s(%d)" % (key,i+1)
                    for v in item2message(_,_prefix,indent+1):
                        yield v
                yield "" # 空白おく

        yield "" # 空白おく

    elif isinstance(item,(unicode,str)) and item:
        yield indentate(u"【%s】%s" % (prefix,item))



def gen_commandNodeTree(scraper_data):
    """ クローラーからコマンドノード生成す"""
    # コマンドノード作る 
    root = ScraperCommand("root",None)

    # クローラーに関連づいたすべてのスクレイパ情報からコマンドツリー作る
    tmp_dict = dict() # { scraper_data : commandNode }
    for scraperInfo_data in ScraperInfoData.objects.filter(scraper=scraper_data, valid=True) :
        # 情報取得
        name = scraperInfo_data.name
        selector = scraperInfo_data.selector
        target = scraperInfo_data.target
        # 再帰クローラー検索
        r_scraper_name = scraperInfo_data.scraper_name
        if r_scraper_name :
            r_scraper = ScraperData.objects.get(name=r_scraper_name) 
        else :
            r_scraper = None

        # コマンド組み立て
        command = gen_command(target,r_scraper,scraper_data.url)
        # フィルタラ組み立て
        filterer = gen_filterer(selector)

        # コマンド起こして一時保管
        tmp_dict[name] = ScraperCommand(name,command,filterer)
        
    # 関連付け
    for key,val in tmp_dict.items():
        # 親読む
        master_scraper = ScraperInfoData.objects.get(scraper=scraper_data, name=key).master_scraper

        # マスターがあればそこにつける
        if master_scraper :
            tmp_dict[master_scraper.name].add_child(val)

        # マスターが無ければルートにつける
        else :
            root.add_child(val)

    return root


def gen_command(target, scraper=None, url_prefix=""):
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
                    if scraper and href :
                        # 絶対パス化
                        href_abs = urlparse.urljoin(url_prefix, href)
                        print href_abs
                        # ノードツリー生成
                        root = gen_commandNodeTree(scraper)
                        # スクレイパ生成
                        _scraper = CommandNodeScraper()
                        _scraper.parse_fromURL(href_abs)
                        # スクレイピング
                        result = _scraper.call(root)
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
def call_webapi(webapi_data):
    """ WebAPIを呼び出す """
    try :
        # データ更新
        webapi_data.refresh_from_db() 
        webapi_data.last_execute_time = timezone.now() # 最終実行時間-> 今
        webapi_data.save()

        # データ抜く
        url = webapi_data.url
        http_method = webapi_data.http_method
        notification = webapi_data.notification

        # パラメーター情報からパラメーター構築
        parameter_data_qs = WebAPIParameterData.objects.filter(webapi=webapi_data) # パラメータデータ
        header_data_qs = WebAPIHttpHeaderParameterData.objects.filter(webapi=webapi_data) # HTTPヘッダ
        param = {} # 送信データ
        headers = {} # HTTPヘッダ
        
        # パラメーターつくる
        for parameter_data in parameter_data_qs:
            name = parameter_data.name
            value = parameter_data.value
            param[name] = value # 構築
        # HTTPヘッダ作る
        for header_data in header_data_qs:
            headers[header_data.name] = header_data.value # 構築
            
        # 送信
        if http_method == "POST" :
            res = requests.post(url, data=param, headers=headers) # POSTする

        elif http_method == "GET":
            res = requests.get(url, data=param, headers=headers) # GETする

        else :
            raise WebAPIException("DELETEメソッドは未実装です")

        # 結果抜いて保存
        data = res.text
        result = WebAPIResultData(
            webapi = webapi_data, 
            result_data = data,
            result = "success"
        )
        result.save()

        notificate_it_forwebAPI(webapi_data,result)
        
    except Exception as e:
        # 結果JSON作成
        data = {
            "status" : "error",
            "message" : reu.decode(str(e)) # エラーメッセージ
        }

        # 結果抜いて保存
        result = WebAPIResultData(
            webapi = webapi_data, 
            result_data = json.dumps(data),
            result="failure"
        )
        result.save()

        notificate_it_forwebAPI(webapi_data,result,True)

    return result


def notificate_it_forwebAPI(webapi_data,result_data,error=False):
    """ 通知するその２"""
    # 通知周りの情報を抜く
    notification = webapi_data.notification.convert2entity() if webapi_data.notification else None # 通知先 : 具象クラスに落とす
    notification_cond = webapi_data.notification_cond # 通知条件

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
        results = WebAPIResultData.objects.filter(webapi=webapi_data).order_by('-datetime')
        if len(results) >=2:
            last_result = results[1] # 1こ前
            last_result_dic = json.loads(last_result.result_data or "") # 辞書に復元
            # 結果比較
            if result_data == last_result_dic :
                return # 一緒なら通知しない

    # メッセージ作成
    jsoned = json.dumps( 
        json.loads(result_data.result_data), # 1回読み込み
        ensure_ascii=False,
        indent=2 # indentつけてdump
        )
    message = (u"WebAPI「%s」を実行しました。\n\n" % (webapi_data.name)) +u"\n" +jsoned

    # 送信
    send_notification(notification,message)


@shared_task
def apply_shcedule():
    """ スケジューリング処理 """
    #now = datetime.datetime.now()
    now = timezone.now()
    # 繰り返しフラグの立つている全クローラを検索
    for scraper_data in ScraperData.objects.all() :
        if scraper_data.repetition :
            # 最終実行時間
            last_execute_time = scraper_data.last_execute_time # エラるのでTZ無視
            repetition = int(scraper_data.repetition) # 繰り返し間隔sec

            # 計算 : 最終実行時間が今からrepetition秒前の時間より前か
            if ( not last_execute_time ) or ( now -last_execute_time > datetime.timedelta(seconds=repetition) ):
                # クローリングする
                do_scrape.delay(scraper_data)
                print "do delay"

    # WEBAPI呼び出しルーチン
    for webapi_data in WebAPIData.objects.all():
        if webapi_data.repetition :
            # 最終実行時間
            last_execute_time = webapi_data.last_execute_time # エラるのでTZ無視
            repetition = int(webapi_data.repetition) # 繰り返し間隔sec

            # 計算 : 最終実行時間が今からrepetition秒前の時間より前か
            if ( not last_execute_time ) or ( now -last_execute_time > datetime.timedelta(seconds=repetition) ):
                # クローリングする
                call_webapi.delay(webapi_data)
                print "do delay"


