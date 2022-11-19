from django.shortcuts import render
import efinance as ef
from datetime import datetime

from nb.models import Shares
from public.response import JsonResponse
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
