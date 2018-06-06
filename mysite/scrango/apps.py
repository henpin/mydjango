# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

URL_PREFIX = "/scrango"

class ScrangoConfig(AppConfig):
    name = 'scrango'


def gen_url(context, pattern):
    """ URL生成 """
    return "/scrango/%s/%s" % (context,pattern)
