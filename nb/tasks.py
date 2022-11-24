#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: tasks.py
# 创建时间: 2022/11/23 0023 11:14
# @Version：V 0.1
# @desc :
import efinance as ef
from celery import Task, shared_task
from django.db.models import Q  # 与或非 查询
from datetime import date, datetime
from chinese_calendar import is_workday

from nb.models import ToDo, Shares, SharesHold
from public.log import logger


@shared_task()
def make_overdue_todo():
    """
    检查过期待办
    """
    now = date.today()
    query = ToDo.objects.filter(Q(is_delete=False) & Q(is_done=0) & Q(end_time__lte=now))
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
def stock_history(name: str, hold_id: str, beg: str, end: str):
    """
    持仓股票历史数据写入
    """
    freq = 15  # 间隔30分钟
    df = ef.stock.get_quote_history([name], klt=freq, beg=beg, end=end)
    if not df:
        logger.error(f"股票 {name} 查询数据为空.{beg}-{end}")
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
        share = Shares.objects.filter(name=key)
        if not share:
            Shares.objects.bulk_create(objs=shares_list)
            logger.info(f"保存成功===>>>{len(shares_list)} 条")


@shared_task()
def stock_today():
    """
    持仓股票当天数据自动写入
    """
    today = date.today()
    year, month, day = today.year, today.month, today.day
    weekday = date(year, month, day).strftime("%A")
    if not is_workday(date(year, month, day)) or weekday in ["Saturday", "Sunday"]:
        logger.info(f"当前时间 {today} 休市日!!!")
        return
    start_time = datetime(year, month, day, 9, 15, 0)
    end_time = datetime(year, month, day, 15, 5, 0)
    am_time = datetime(year, month, day, 11, 35, 0)
    pm_time = datetime(year, month, day, 13, 00, 0)
    now_time = datetime.now()
    if now_time < start_time or now_time > end_time or am_time < now_time < pm_time:
        logger.info(f"当前时间 {now_time} 未开盘!!!")
        return
    hold_list = SharesHold.objects.filter(is_delete=False)
    stock_list = list()
    stock_dict = dict()
    for hold in hold_list:
        stock_list.append(hold.name)
        stock_dict.update({hold.name: hold.id})
    freq = 1
    df = ef.stock.get_quote_history(["宝鹰股份"], klt=freq)
    if not df:
        logger.error(f"持仓股票 {stock_list} 查询数据为空.")
        return
    for key, value in df.items():
        share_list = Shares.objects.filter(name=key).order_by("-date_time")
        base_date_time = share_list[0].date_time
        df_list = value.to_dict(orient="records")
        shares_list = []
        new_price = 0
        for data in df_list:
            date_time = data["日期"]
            new_price = data["收盘"]
            if date_time <= base_date_time:
                continue
            obj = Shares(
                name=key, code=data["股票代码"], date_time=data["日期"], open_price=data["开盘"],
                new_price=data["收盘"], top_price=data["最高"], down_price=data["最低"], turnover=data["成交量"],
                business_volume=data["成交额"], amplitude=data["振幅"], rise_and_fall=data["涨跌幅"],
                rise_and_price=data["涨跌额"], turnover_rate=data["换手率"], shares_hold_id=stock_dict[key]
            )
            shares_list.append(obj)
        try:
            hold = SharesHold.objects.get(id=stock_dict[key])

            hold.profit_and_loss = round(hold.number * float(new_price) - hold.number * hold.cost_price, 2)
            hold.save()
        except Exception as error:
            logger.error(f"更新持仓盈亏出现错误. ===>>> {error}")
            return
        share = Shares.objects.filter(Q(name=key) & Q(date_time__gt=base_date_time))
        if not share:
            Shares.objects.bulk_create(objs=shares_list)
            logger.info(f"保存成功===>>>{len(shares_list)} 条")
