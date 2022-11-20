#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: views_api.py
# 创建时间: 2022/11/20 0020 11:13
# @Version：V 0.1
# @desc :
import efinance as ef
import json
from django.shortcuts import render
from datetime import datetime
from django.forms.models import model_to_dict
from django.db.models import Q  # 与或非 查询
from django.core.cache import cache

from nb.models import Shares, Poetry
from public.response import JsonResponse
from public.recommend import recommend_handle, surplus_second
from public.conf import GET, POST, RECOMMEND
from public.auth_token import auth_token
from public.log import logger


def shares(request, beg, end):
    # 股票代码
    stock_code = ["宝鹰股份"]
    # 数据间隔时间为 5 分钟
    freq = 5
    # 获取最新一个交易日的分钟级别股票行情数据
    df = ef.stock.get_quote_history(stock_code, klt=freq, beg=beg, end=end)
    if not df:
        return JsonResponse.BadRequest(message="查询数据为空.")

    for key, value in df.items():
        df_list = value.to_dict(orient="records")
        shares_list = []
        for data in df_list:
            obj = Shares(
                name=data["股票名称"], code=data["股票代码"], date_time=data["日期"], open_price=data["开盘"],
                new_price=data["收盘"], top_price=data["最高"], down_price=data["最低"], turnover=data["成交量"],
                business_volume=data["成交额"], amplitude=data["振幅"], rise_and_fall=data["涨跌幅"],
                rise_and_price=data["涨跌额"], turnover_rate=data["换手率"]
            )
            shares_list.append(obj)
        share = Shares.objects.filter(name="宝鹰股份")
        if not share:
            Shares.objects.bulk_create(objs=shares_list)
            logger.info(f"保存成功===>>>{len(shares_list)} 条")
    return JsonResponse.OK()


def recommend_poetry(request):
    if request.method == GET:
        result = cache.get(RECOMMEND)
        if not result:
            poetry_type = recommend_handle()
            # 随机返回一条数据 filter 等于  exclude 不等于
            poetry = Poetry.objects.filter(type=poetry_type).exclude(phrase="").order_by('?').first()
            result = {
                "poetry_name": poetry.name,
                "type": poetry.type,
                "phrase": poetry.phrase,
            }
            if poetry.author:
                result.update({
                    "author": poetry.author.name,
                    "dynasty": poetry.author.dynasty,
                })
            second = surplus_second()
            cache.set("RECOMMEND", result, second)
        return JsonResponse.OK(data=result)
