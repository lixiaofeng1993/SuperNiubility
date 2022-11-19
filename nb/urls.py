#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: urls.py
# 创建时间: 2022/11/19 0019 21:34
# @Version：V 0.1
# @desc :
from django.urls import path

from nb import views

urlpatterns = [
    path("shares/<str:beg>/<str:end>", views.shares, name="shares"),
]
