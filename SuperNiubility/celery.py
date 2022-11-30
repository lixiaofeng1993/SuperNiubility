#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: celery.py
# 创建时间: 2022/11/23 0023 11:07
# @Version：V 0.1
# @desc :
from __future__ import absolute_import, unicode_literals
from celery import Celery, platforms
from django.conf import settings
from celery.schedules import crontab
import os

platforms.C_FORCE_ROOT = True
# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SuperNiubility.settings')

# 注册Celery的APP
app = Celery('SuperNiubility')
# 绑定配置文件
app.config_from_object('django.conf:settings')

# 自动发现各个app下的tasks.py文件
# app.autodiscover_tasks(['page'], force=True)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
