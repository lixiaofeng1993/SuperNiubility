#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: tasks.py
# 创建时间: 2022/11/23 0023 11:14
# @Version：V 0.1
# @desc :
from celery import Task, shared_task
from django.db.models import Q  # 与或非 查询

from nb.models import ToDo, Shares
from public.stock_api import ef, delete_cache, etc_time, cache, StockEndTime, stock_today, stock_buy_sell, stock_inflow, \
    stock_holder as holder, stock_sector, stock_holder_number, stock_super
from public.log import logger


@shared_task()
def make_overdue_todo():
    """
    检查过期待办
    """
    moment = etc_time()
    query = ToDo.objects.filter(Q(is_delete=False) & Q(is_done=0) & Q(end_time__lte=moment["today"]))
    if not query:
        logger.info("没有需要修改的todo列表数据.")
        return
    for td in query:
        td.is_done = 2
    try:
        ToDo.objects.bulk_update(query, ["is_done"])
        logger.info("批量修改todo列表数据完成.")
    except Exception as error:
        logger.error(f"批量修改todo列表数据出现异常 ===>>> {error}")


@shared_task()
def stock_history(code: str, hold_id: str, user_id, beg: str, end: str, last_day_time: str):
    """
    持仓股票历史数据写入
    """
    freq = 15  # 间隔15分钟
    df = ef.stock.get_quote_history([code], klt=freq, beg=beg, end=end)
    if not df:
        logger.error(f"股票 {code} 查询数据为空.{beg}-{end}")
        return
    for key, value in df.items():
        df_list = value.to_dict(orient="records")
        shares_list = []
        for data in df_list:
            obj = Shares(
                name=data["股票名称"], code=data["股票代码"], date_time=data["日期"], open_price=data["开盘"],
                new_price=data["收盘"], top_price=data["最高"], down_price=data["最低"], turnover=data["成交量"],
                business_volume=data["成交额"], amplitude=data["振幅"], rise_and_fall=data["涨跌幅"],
                rise_and_price=data["涨跌额"], turnover_rate=data["换手率"], shares_hold_id=hold_id
            )
            shares_list.append(obj)
        if last_day_time:
            share = Shares.objects.filter(Q(code=code) &
                                          Q(shares_hold_id=hold_id)).exclude(date_time__contains=last_day_time).exists()
        else:
            share = Shares.objects.filter(Q(code=code) & Q(shares_hold_id=hold_id)).exists()
        if not share:
            Shares.objects.bulk_create(objs=shares_list)
            delete_cache(user_id, hold_id)  # 导入成功，删除缓存
            logger.info(f"{key} 保存成功===>>>{len(shares_list)} 条")


@shared_task()
def last_day_stock_history(code: str, hold_id: str, user_id):
    """
    持仓股票最近一天数据写入
    """
    freq = 1  # 间隔1分钟
    df = ef.stock.get_quote_history(code, klt=freq)
    if df.empty:
        logger.error(f"股票 {code} 查询数据为空.")
        return
    shares_list = list()
    now_time = ""
    for key, value in df.iterrows():
        now_time = value["日期"].split(" ")[0]
        obj = Shares(
            name=value["股票名称"], code=value["股票代码"], date_time=value["日期"], open_price=value["开盘"],
            new_price=value["收盘"], top_price=value["最高"], down_price=value["最低"], turnover=value["成交量"],
            business_volume=value["成交额"], amplitude=value["振幅"], rise_and_fall=value["涨跌幅"],
            rise_and_price=value["涨跌额"], turnover_rate=value["换手率"], shares_hold_id=hold_id
        )
        shares_list.append(obj)
    share = Shares.objects.filter(Q(code=code) & Q(shares_hold_id=hold_id)).exclude(
        date_time__contains=now_time).exists()
    if not share:
        Shares.objects.bulk_create(objs=shares_list)
        delete_cache(user_id, hold_id)  # 导入成功，删除缓存
        cache.set(StockEndTime.format(user_id=user_id), True, 20)
        logger.info(f"{code} 保存成功===>>>{len(shares_list)} 条")


@shared_task()
def stock():
    """
    定时写入股票数据
    """
    stock_today()
    stock_buy_sell()
    stock_inflow()
    stock_sector()


@shared_task()
def stock_holder():
    holder()
    stock_holder_number()
    stock_super()
