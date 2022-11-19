#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: response.py
# 创建时间: 2022/11/19 0019 23:47
# @Version：V 0.1
# @desc :
import json
from django.http import HttpResponse


class JsonResponse(HttpResponse):
    def __init__(self, code=200, message="ok", data=None):
        response = dict()
        response["code"] = code
        response["message"] = message
        response["data"] = data
        super(JsonResponse, self).__init__(json.dumps(response, ensure_ascii=False), content_type="application/json", )

    @staticmethod
    def OK(message="ok", data=None):
        response = JsonResponse(200, message, data)
        return response

    @staticmethod
    def BadRequest(message="请求出现异常.", data=None):
        response = JsonResponse(400, message, data)
        return response

    @staticmethod
    def Unauthorized(message="没有权限.", data=None):
        return JsonResponse(401, message, data)

    @staticmethod
    def MethodNotAllowed(message="请求方式错误.", data=None):
        return JsonResponse(405, message, data)

    @staticmethod
    def ServerError(message="系统异常.", data=None):
        return JsonResponse(500, message, data)
