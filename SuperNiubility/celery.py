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

# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SuperNiubility.settings')

# 注册Celery的APP
app = Celery('SuperNiubility')
# 绑定配置文件
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现各个app下的tasks.py文件
# app.autodiscover_tasks(['page'], force=True)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'make_overdue_todo': {
        # 任务路径
        'task': 'nb.tasks.make_overdue_todo',
        'schedule': crontab(minute=59, hour=23),
        # 'schedule': 5,
        'args': (),
    },
    'stock_today': {
        # 任务路径
        'task': 'nb.tasks.stock_today',
        'schedule': 5 * 60,
        'args': (),
    },
    'stock_detail': {
        # 任务路径
        'task': 'nb.tasks.stock_detail',
        'schedule': 6 * 60,
        'args': (),
    },
}
