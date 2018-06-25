# -*- coding: utf-8 -*-

from tinydb import TinyDB

"""
flask-tinyDBクライアント
"""

DB = TinyDB('myflask.json')

class BaseMyTinyTable(object):
    table = None

    def insert(self,*args,**kwargs):
        """ 汎用インサート """
        return self.table.insert(*args,**kwargs)

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
            "data-type" : "format"
        })
    
    def insert_data(self,json,name="default"):
        """ データインサート """
        self.insert({
            "name" : name,
            "json" : json,
            "data-type" : "data"
        })
        
