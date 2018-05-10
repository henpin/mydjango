# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import Celery
from django.conf import settings
import os

"""
セロリをつかった非同期タスク
"""

# Settings
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery('mysite')
#CELERY_TIMEZONE = 'UTC'
app.config_from_object('django.conf:settings')

app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
)

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
