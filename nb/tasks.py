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

from nb.models import ToDo, Shares, SharesHold, StockDetail
from public.common import delete_cache, check_stoke_date, etc_time, cache, StockEndTime, difference_stock, datetime, \
    message_writing, MessageBuySell, MessageToday
from public.send_ding import send_ding
from public.stock_api import stock_api
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
            delete_cache(user_id)  # 导入成功，删除缓存
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
        delete_cache(user_id)  # 导入成功，删除缓存
        cache.set(StockEndTime.format(user_id=user_id), True, 20)
        logger.info(f"{code} 保存成功===>>>{len(shares_list)} 条")


@shared_task()
def stock_today():
    """
    持仓股票当天数据自动写入
    每五分钟写入一次
    """
    moment = check_stoke_date()
    if not moment:  # 判断股市开关时间
        return
    hold_list = SharesHold.objects.filter(is_delete=False)
    stock_list = list()
    stock_dict = dict()
    for hold in hold_list:
        stock_list.append(hold.code)
        stock_dict.update({hold.code: hold.id})
    freq = 1
    df = ef.stock.get_quote_history(stock_list, klt=freq)
    if not df:
        logger.error(f"持仓股票 {stock_list} 查询数据为空.")
        return
    for key, value in df.items():
        shares = Shares.objects.filter(
            Q(code=key) & Q(shares_hold_id=stock_dict[key])).order_by("-date_time").first()
        base_date_time = shares.date_time
        df_list = value.to_dict(orient="records")
        shares_list = []
        new_price = 0
        for data in df_list:
            date_time = data["日期"]
            new_price = data["收盘"]
            if date_time <= base_date_time:  # 避免重复写入
                continue
            obj = Shares(
                name=data["股票名称"], code=key, date_time=data["日期"], open_price=data["开盘"],
                new_price=data["收盘"], top_price=data["最高"], down_price=data["最低"], turnover=data["成交量"],
                business_volume=data["成交额"], amplitude=data["振幅"], rise_and_fall=data["涨跌幅"],
                rise_and_price=data["涨跌额"], turnover_rate=data["换手率"], shares_hold_id=stock_dict[key]
            )
            shares_list.append(obj)
        try:
            hold = SharesHold.objects.get(id=stock_dict[key])
            is_profit = hold.is_profit
            hold.is_profit = True if hold.profit_and_loss > 0 else False
            if hold.number and hold.cost_price and moment["stock_time"] > hold.update_date:
                hold.profit_and_loss = round(hold.number * float(new_price) - hold.number * hold.cost_price, 2)
                hold.today_price = round((float(new_price) - hold.last_close_price) * hold.number, 2)
                if moment["now"] >= moment["stock_time"]:
                    hold.last_close_price = new_price
                    hold.last_day = moment["today"]
                    hold.days += 1
                hold.save()
            if is_profit != hold.is_profit:
                if hold.is_profit:
                    profit_text = "亏转盈"
                    color = "#FF0000"
                else:
                    profit_text = "盈转亏"
                    color = "#00FF00"
                body = {
                    "msgtype": "markdown",
                    "markdown": {
                        "title": hold.name,
                        "text": f"### {hold.name}\n\n"
                                f"> **{profit_text}** <font color={color}>{hold.profit_and_loss}</font> 元\n\n"
                                f"> **点击查看** [股票分析](http://121.41.54.234/nb/stock/)@15235514553"
                    },
                    "at": {
                        "atMobiles": ["15235514553"],
                        "isAtAll": False,
                    }}
                send_ding(body)
        except Exception as error:
            logger.error(f"更新持仓盈亏出现错误. ===>>> {error}")
            return
        share = Shares.objects.filter(
            Q(code=key) & Q(date_time__gt=base_date_time) & Q(shares_hold_id=hold.id)).exists()
        if not share:
            Shares.objects.bulk_create(objs=shares_list)
            message_writing(MessageToday)
            logger.info(f"保存成功===>>>{len(shares_list)} 条")


@shared_task()
def stock_detail(flag=True):
    moment = check_stoke_date()
    if not moment and flag:  # 判断股市开关时间
        return
    hold = SharesHold.objects.filter(Q(is_delete=False) & Q(is_detail=True)).first()
    if not hold:
        logger.error("未设置 is_detail 字段.")
        return
    code = difference_stock(code=hold.code)
    result = stock_api(code=code)
    if not result:
        return
    response = result["data"]
    dapandata = result["dapandata"]
    gopicture = result["gopicture"]
    change = {
        'traAmount': 'nowTraAmount',
        'traNumber': 'nowTraNumber'
    }
    response.update(gopicture)
    date_time = f'{response["date"]} {response["time"]}'
    check_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    detail = StockDetail.objects.filter(Q(is_delete=False) &
                                        Q(code=code) & Q(shares_hold_id=hold.id)).order_by("-time").first()
    if detail and check_time <= detail.time:  # 判重
        logger.info(f"股票详情表数据重复.===>>>{check_time} {detail.time}")
        return
    dapandata_dict = dict()
    for key, value in dapandata.items():
        if key in change.keys():
            dapandata_dict.update({change[key]: value})
        else:
            dapandata_dict.update({key: value})
    response.update(dapandata_dict)
    detail_obj = StockDetail(
        name=response["name"], code=code, increPer=response["increPer"], increase=response["increase"],
        todayStartPri=response["todayStartPri"], yestodEndPri=response["yestodEndPri"], nowPri=response["nowPri"],
        todayMax=response["todayMax"], todayMin=response["todayMin"], competitivePri=response["competitivePri"],
        reservePri=response["reservePri"], traNumber=response["traNumber"], traAmount=response["traAmount"],
        buyOne=response["buyOne"], buyOnePri=response["buyOnePri"], buyTwo=response["buyTwo"],
        buyTwoPri=response["buyTwoPri"], buyThree=response["buyThree"], buyThreePri=response["buyThreePri"],
        buyFour=response["buyFour"], buyFourPri=response["buyFourPri"], buyFive=response["buyFive"],
        buyFivePri=response["buyFivePri"], sellOne=response["sellOne"], sellOnePri=response["sellOnePri"],
        sellTwo=response["sellTwo"], sellTwoPri=response["sellTwoPri"], sellThree=response["sellThree"],
        sellThreePri=response["sellThreePri"], sellFour=response["sellFour"], sellFourPri=response["sellFourPri"],
        sellFive=response["sellFive"], sellFivePri=response["sellFivePri"], date=response["date"],
        time=date_time, dot=response["dot"], nowPic=response["nowPic"], rate=response["rate"],
        nowTraAmount=response["nowTraAmount"], nowTraNumber=response["nowTraNumber"], minurl=response["minurl"],
        dayurl=response["dayurl"], weekurl=response["weekurl"], monthurl=response["monthurl"],
        shares_hold_id=hold.id,
    )
    try:
        if hold.number and hold.cost_price and moment["stock_time"] > hold.update_date:
            hold.profit_and_loss = round(hold.number * float(response["dot"]) - hold.number * hold.cost_price, 2)
            hold.today_price = round((float(response["dot"]) - hold.last_close_price) * hold.number, 2)
            if moment["now"] >= moment["stock_time"]:
                hold.last_close_price = response["dot"]
                hold.last_day = moment["today"]
                hold.days += 1
            hold.save()
        detail_obj.save()
        message_writing(MessageBuySell)
        logger.info("股票详情保存成功.")
    except Exception as error:
        logger.error(f"股票详情保存失败 ===>>> {error}")
