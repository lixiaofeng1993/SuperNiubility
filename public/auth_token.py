#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: auth_token.py
# 创建时间: 2022/11/20 0020 15:56
# @Version：V 0.1
# @desc :
from django.core.cache import cache

from public.jwt_sign import get_current_user
from public.response import JsonResponse


def auth_token():
    def wrap1(view_func):  # page_cache装饰器
        def wrap2(request, *args, **kwargs):
            access_token = request.META.get("HTTP_AUTHORIZATION")  # Authorization
            username = get_current_user(token=access_token)
            token = cache.get(username)
            if access_token and token and access_token == token:
                response = view_func(request, *args, **kwargs)
                return response
            else:
                return JsonResponse.Unauthorized()

        return wrap2

    return wrap1
