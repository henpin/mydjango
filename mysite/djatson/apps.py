# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class DjatsonConfig(AppConfig):
    name = 'djatson'

def gen_url(context, pattern):
    """ URL生成 """
    if context == "chat":
        return "/djatson/kaminaga/chat/"+pattern
    """
    elif context == "js":
        return "/djangolla/kaminaga/"+pattern+".js"
    elif context == "replay_html":
        return "/djangolla/kaminaga/replay/"+pattern
    """
