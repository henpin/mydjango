# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class DjangollaConfig(AppConfig):
    name = 'djangolla'

def gen_url(context, pattern):
    """ URL生成 """
    if context == "html":
        return "/djangolla/kaminaga/demo/"+pattern
    elif context == "js":
        return "/djangolla/kaminaga/"+pattern+".js"
    elif context == "replay_html":
        return "/djangolla/kaminaga/replay/"+pattern
        
