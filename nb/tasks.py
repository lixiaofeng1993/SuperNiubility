#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: tasks.py
# 创建时间: 2022/11/23 0023 11:14
# @Version：V 0.1
# @desc :

from celery import Task, shared_task
from django.db.models import Q  # 与或非 查询
from datetime import date

from nb.models import ToDo
from public.log import logger


@shared_task()
def make_overdue_todo():
    now = date.today()
    query = ToDo.objects.filter(Q(is_delete=False) & Q(is_done=0) & Q(end_time__lte=now))
    if query:
        for td in query:
            td.is_done = 2
        try:
            ToDo.objects.bulk_update(query, ["is_done"])
            logger.info("批量修改todo列表数据完成.")
        except Exception as error:
            logger.error(f"批量修改todo列表数据出现异常 ===>>> {error}")
