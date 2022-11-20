#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: urls.py
# 创建时间: 2022/11/19 0019 21:34
# @Version：V 0.1
# @desc :
from django.urls import path

from nb import views, views_api

urlpatterns = [

    path("shares/<str:beg>/<str:end>", views_api.shares, name="shares"),
    path("poetry/random/", views_api.recommend_poetry, name="poetry_random"),
]
