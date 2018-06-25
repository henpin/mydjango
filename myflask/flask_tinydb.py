# -*- coding: utf-8 -*-

from tinydb import TinyDB, Query

"""
flask-tinyDBクライアント
"""

DB = TinyDB('myflask.json')

class BaseMyTinyTable(object):
    table = None

    def insert(self,*args,**kwargs):
        """ 汎用インサート """
        return self.table.insert(*args,**kwargs)

    def search(self,*args,**kwargs):
        """ 検索 """
        return self.table.search(*args,**kwargs)

    def all(self,_type):
        if _type :
            que = Query()
            return self.search(que.data_type == _type)
        else :
            return self.table.all()

class PDFFormDB(BaseMyTinyTable):
    """ PDFフォーム用DB """
    # テーブル
    table = DB.table("pdf_form")

    def insert_format(self,json,name="default"):
        """ フォーマットJSONデータ入れる"""
        # インサート
        self.insert({
            "name" : name,
            "json" : json,
            "data_type" : "format"
        })
    
    def insert_data(self,_uuid,json,png_file=None,name="default"):
        """ データインサート """
        self.insert({
            "name" : name,
            "uuid" : _uuid,
            "json" : json,
            "png_file" : png_file,
            "data_type" : "data"
        })

    def search_data(self,_uuid):
        """ UUIDで検索 """
        que = Query()
        print _uuid
        result = self.search(
            (que.uuid == _uuid) & (que.data_type == "data")
            )
        print result
        return result and result[-1]
