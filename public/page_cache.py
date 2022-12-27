#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: page_cache.py
# 创建时间: 2022/11/24 0024 18:31
# @Version：V 0.1
# @desc :
from django.core.cache import cache
from public.log import logger


def page_cache(timeout):
    def wrap1(view_func):  # page_cache装饰器
        def wrap2(request, *args, **kwargs):
            key = 'Response-{}'.format(request.get_full_path())  # 拼接唯一的key
            response = cache.get(key)  # 从缓存中获取数据
            logger.info('url -> {} 从缓存中获取数据 -> {}'.format(key, response))
            if response is None:
                # 获取数据库中的数据,添加到缓存中
                response = view_func(request, *args, **kwargs)
                cache.set(key, response, timeout)
                logger.info('url -> {} 从数据库中获取 -> {}'.format(key, response))
            return response

        return wrap2

    return wrap1
