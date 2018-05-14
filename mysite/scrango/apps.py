# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

URL_PREFIX = "/scrango"

class ScrangoConfig(AppConfig):
    name = 'scrango'


def gen_url(context, pattern):
    """ URL生成 """
    if context == "scrape":
        return URL_PREFIX +"/kaminaga/scrape/"+pattern
