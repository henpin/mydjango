# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class DjatsonConfig(AppConfig):
    name = 'djatson'


def gen_url(context, pattern):
    """ URL生成 """
    return "/djatson/%s/%s" % (context,pattern)

