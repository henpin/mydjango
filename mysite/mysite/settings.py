# -*- coding: utf-8 -*-
"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 1.11.12.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/

---------------------------------------------------------------------
Addtional apps :
* bootstrap_admin : admin装飾テーマ
* django_admin_row_actions : actionを行ごとに表示してくれる
    * https://github.com/DjangoAdminHackers/django-admin-row-actions
* jet : admin装飾テーマ
"""

import os
from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's#9kkdi@denkmc^l136clxsdtds4%u$ppde06@cghz_pu4!&)='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
#DEBUG = False

ALLOWED_HOSTS = [
    "localhost",
    "52.197.80.112"
]


# Application definition
INSTALLED_APPS = [
    'polls.apps.PollsConfig',
    'djangolla.apps.DjangollaConfig',
    'djatson.apps.DjatsonConfig',
    'scrango.apps.ScrangoConfig',
    'jet.dashboard', # django-jet
    'jet', # django-jet
    #'bootstrap_admin', # commentout if theme not installed
    'django_admin_row_actions', # commentout if theme not installed
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djcelery', # Async-processing-framework
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': { # for mysql
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mydjango',
        'USER': 'mydjango',
        'PASSWORD': 'Emma#2017',
        'HOST': 'scrango.c21zunpjfeom.ap-northeast-1.rds.amazonaws.com',
    },
    'sqlite': { # for sqlite
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
SILENCED_SYSTEM_CHECKS = ['mysql.E001'] # TODO : ワーニングをもみ消す


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# setting django-celery
import djcelery

# スケジューリング
CELERYBEAT_SCHEDULE = {
    'add-every-30-seconds': {
        'task': 'scrango.tasks.apply_shcedule',
        'schedule': timedelta(seconds=30),
        #'args': (16, 16)
    },
}

djcelery.setup_loader()


# settings media
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# JET
#JET_SIDE_MENU_COMPACT = True

