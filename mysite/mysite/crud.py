# -*- coding: utf-8 -*-
from crudbuilder.abstract import BaseCrudBuilder
from scrango.models import CrawlerData, ScraperData, ResultData, ActionData
from scrango.models import ChatAPIData, SlackAPIData, ChatworkAPIData

class CrawlerDataCrud(BaseCrudBuilder):
    """ クローラーデータのくらっど"""
    model = CrawlerData
    search_fields = ['name']
    tables2_fields = ('name',)
    modelform_excludes = []
    login_required=True
    permission_required=True

