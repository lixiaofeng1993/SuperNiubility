#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: urls.py
# 创建时间: 2022/11/27 0027 15:23
# @Version：V 0.1
# @desc :
from django.urls import path

from wx import views

urlpatterns = [
    path("", views.WechatServe.as_view(), name="wx"),
]
