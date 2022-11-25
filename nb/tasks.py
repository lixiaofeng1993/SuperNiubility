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

from nb.models import ToDo, Shares, SharesHold
from public.common import delete_cache, check_stoke_date, etc_time
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
def stock_history(code: str, hold_id: str, beg: str, end: str):
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
        share = Shares.objects.filter(name=key)
        if not share:
            Shares.objects.bulk_create(objs=shares_list)
            delete_cache()  # 导入成功，删除缓存
            logger.info(f"保存成功===>>>{len(shares_list)} 条")


@shared_task()
def stock_today():
    """
    持仓股票当天数据自动写入
    每五分钟写入一次
    """
    if not check_stoke_date():  # 判断股市开关时间
        return
    hold_list = SharesHold.objects.filter(is_delete=False)
    stock_list = list()
    stock_dict = dict()
    for hold in hold_list:
        stock_list.append(hold.code)
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
            if date_time <= base_date_time:  # 避免重复写入
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
            if hold.number and hold.cost_price:
                hold.profit_and_loss = round(hold.number * float(new_price) - hold.number * hold.cost_price, 2)
                hold.today_price = round((float(new_price) - hold.last_close_price) * hold.number, 2)
                moment = etc_time()
                if moment["now"] >= moment["end_time"]:
                    hold.last_close_price = new_price
                hold.save()
        except Exception as error:
            logger.error(f"更新持仓盈亏出现错误. ===>>> {error}")
            return
        share = Shares.objects.filter(Q(name=key) & Q(date_time__gt=base_date_time))
        if not share:
            Shares.objects.bulk_create(objs=shares_list)
            logger.info(f"保存成功===>>>{len(shares_list)} 条")
