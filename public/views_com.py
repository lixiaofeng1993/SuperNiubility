#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: views_com.py
# 创建时间: 2022/12/25 0025 11:45
# @Version：V 0.1
# @desc :
import efinance as ef
from django.contrib.admin.models import LogEntry, CHANGE, ADDITION, DELETION
from django.contrib.admin.options import get_content_type_for_model

from nb.models import Poetry, Message, StockDetail, InflowStock, ShareholderNumber
from public.send_ding import profit_and_loss, profit_and_loss_ratio, limit_up
from public.recommend import recommend_handle
from public.common import *


def home_poetry():
    """
    诗词推荐列表
    """
    count = cache.get(APICount)
    flag = False
    if count and count < APICountNumber:
        count += 1
        flag = True
        cache.set(APICount, count, surplus_second())
    elif count and count >= APICountNumber:
        flag = False
    else:
        cache.set(APICount, 1, surplus_second())
    poetry_type = recommend_handle(flag)
    # 随机返回一条数据 filter 等于  exclude 不等于
    poetry_list = Poetry.objects.filter(type=poetry_type).exclude(phrase="").order_by('?')[:HomeNumber]
    obj_list = list()
    for poetry in poetry_list:
        result = {
            "id": str(poetry.id),
            "poetry_name": poetry.name,
            "type": poetry.type,
            "phrase": poetry.phrase,
        }
        if poetry.author:
            result.update({
                "author": poetry.author.name,
                "dynasty": poetry.author.dynasty,
            })
        obj_list.append(result)
    logger.info("查询诗词推荐列表 ===>>> 成功.")
    cache.set(RECOMMEND, obj_list, surplus_second())
    return obj_list


def handle_tar_number(stock_id: str):
    """
    处理成交量
    """
    data_list = list()
    labels = list()
    detail_list = StockDetail.objects.filter(Q(is_delete=False) &
                                             Q(shares_hold_id=stock_id) &
                                             Q(time__hour=15)).order_by("time")
    diff_list = list()
    for detail in detail_list:
        date_time = str(detail.time).split(" ")[0]
        if date_time not in diff_list:
            diff_list.append(date_time)
            data_list.append(round(detail.traNumber / 10000, 2))
            labels.append(date_time)
    return data_list, labels


def regularly_hold(hold, moment: dict, price: float, old_price: float):
    """
    实时更新 持有股票收益
    """
    is_profit = hold.is_profit = True if hold.profit_and_loss > 0 else False
    hold.profit_and_loss = round(hold.number * float(price) - hold.number * hold.cost_price, 2)
    old_price = old_price if hold.days else hold.last_close_price
    hold.today_price = round((float(price) - old_price) * hold.number, 2)
    if hold.cost_price:
        if moment["now"] <= moment["stock_time"]:
            profit_and_loss_ratio(hold, price)
        hold.last_close_price = price
        hold.last_day = moment["today"]
        if moment["now"] >= moment["stock_time"] > hold.update_date:
            hold.days += 1
    try:
        hold.save()
        logger.info(f"实时更新 持有股票 {hold.name} 收益 保存成功！")
        return is_profit
    except Exception as error:
        logger.error(f"实时更新 持有股票收益 保存报错！===>>> {error}")


def message_writing(name: str, user_id, stock_id: str, date_time: datetime, link_type: str):
    """
    写入消息提醒
    """
    try:
        cache.delete(TodayChart.format(user_id=user_id))
        cache.delete(TodayStockChart.format(stock_id=stock_id))
        cache.delete(TodayBuySellChart.format(stock_id=stock_id))
        cache.delete(TodayKDJChart.format(user_id=user_id))
        cache.delete(TodayInflowChart.format(stock_id=stock_id))
        cache.delete(TodayPrice.format(stock_id=stock_id))
        message = Message()
        message.name = name
        message.obj_id = stock_id
        message.date = date_time
        message.type = link_type
        message.save()
        logger.info("写入消息提醒成功.")
    except Exception as error:
        logger.error(f"写入消息提醒出现异常===>>>{error}")


def operation_record(request, model, model_id, repr, action_flag, msg: str = ""):
    """
    操作记录
    删除 action_flag: del
    添加、编辑 model_id
    剩余操作 model_id， msg
    """
    if not action_flag:
        action_flag = CHANGE if model_id else ADDITION
        if not msg:
            change_message = f"编辑{repr} {model.name}" if model_id else f"添加{repr} {model.name}"
        else:
            change_message = msg
    elif action_flag == "del":
        action_flag = DELETION
        change_message = f"删除{repr} {model.name}"
    elif action_flag == "change":
        action_flag = CHANGE
        change_message = f"查看{repr} {model_id}"
    user_id = request.session["user_id"] if request.session.get("user_id") else model.id
    LogEntry.objects.log_action(
        user_id=user_id,
        content_type_id=get_content_type_for_model(model).id,
        object_id=model.id,
        object_repr=repr,
        action_flag=action_flag,
        change_message=change_message,
    )


def stock_home(obj_list: list):
    """
    股票页面展示数据处理
    """
    data_list = list()
    for obj in obj_list:
        if obj.cost_price:
            detail = StockDetail.objects.filter(Q(is_delete=False) & Q(shares_hold_id=obj.id)).order_by("-time").first()
            if not detail:
                data_list.append(obj)
            else:
                data_list.append({
                    "name": obj.name,
                    "code": obj.code,
                    "total_price": round(detail.nowPri * obj.number, 2),
                    "now_price": detail.nowPri,
                    "number": obj.number,
                    "profit_and_loss": obj.profit_and_loss,
                    "cost_price": obj.cost_price,
                    "hold_rate": str(round(obj.profit_and_loss / (obj.cost_price * obj.number) * 100, 3)) + "%",
                    "today_price": obj.today_price,
                    "today_rate": str(round(obj.today_price / (detail.nowPri * obj.number) * 100, 3)) + "%",
                    "days": obj.days,
                    "id": obj.id
                })
        else:
            data_list.append(obj)
    return data_list


def handle_detail_data(stock_id: str):
    """
    处理股票详情数据
    """
    detail = StockDetail.objects.filter(Q(is_delete=False) & Q(shares_hold_id=stock_id)).order_by("-time").first()
    data = {
        "todayStartPri": {
            "todayStartPri": detail.todayStartPri,
            "color": font_color_two(detail.todayStartPri, detail.yestodEndPri),
        }, "nowPri": {
            "nowPri": detail.nowPri,
            "color": font_color_two(detail.nowPri, detail.yestodEndPri),
        }, "avg_price": {
            "avg_price": detail.avg_price,
            "color": font_color_two(detail.avg_price, detail.yestodEndPri),
        }, "todayMax": {
            "todayMax": detail.todayMax,
            "color": font_color_two(detail.todayMax, detail.yestodEndPri),
        }, "todayMin": {
            "todayMin": detail.todayMin,
            "color": font_color_two(detail.todayMin, detail.yestodEndPri),
        }, "increPer": {
            "increPer": detail.increPer,
            "color": font_color(detail.increPer),
        }, "increase": {
            "increase": detail.increase,
            "color": font_color(detail.increase),
        },
        "top_price": detail.top_price,
        "down_price": detail.down_price,
        "turnover_rate": detail.turnover_rate,
        "industry": detail.industry,
        "P_E_ratio_dynamic": detail.P_E_ratio_dynamic,
        "ROE_ratio": handle_rate(detail.ROE_ratio),
        "traNumber": handle_price(detail.traNumber),
        "traAmount": handle_price(detail.traAmount),
        "yestodEndPri": detail.yestodEndPri,
        "section_no": detail.section_no,
        "net_profit": handle_price(detail.net_profit),
        "total_market_value": handle_price(detail.total_market_value),
        "circulation_market_value": handle_price(detail.circulation_market_value),
        "gross_profit_margin": handle_rate(detail.gross_profit_margin),
        "net_interest_rate": handle_rate(detail.net_interest_rate),
    } if detail else {}
    return data


def inflow_forecast(small_price, big_price, middle_price, huge_price, today_price):
    """
    流入流出预测
    """
    just_price = 0
    reduce_price = 0

    def add_price(pri: float):
        nonlocal just_price, reduce_price
        if pri > 0:
            just_price += pri
        elif pri < 0:
            reduce_price += pri

    add_price(small_price)
    add_price(big_price)
    add_price(big_price)
    add_price(middle_price)
    add_price(huge_price)
    if small_price > 0:
        small_rate = round(small_price / just_price * 100, 2)
    elif small_price < 0:
        small_rate = -round(small_price / reduce_price * 100, 2)
    else:
        small_rate = 0
    if today_price > 0:
        text = f"主力流入, 小散流入占比 {small_rate} %；"
        color = "red"
    elif today_price < 0:
        text = f"主力流出, 小散流入占比 {small_rate} %；"
        color = "green"
    else:
        text = ""
        color = ""
    return text, color


def handle_inflow_data(stock_id: str):
    """
    处理资金流入流出数据
    """
    moment = check_stoke_day()
    price, small, big, middle, huge = 0, 0, 0, 0, 0
    small_price, big_price, middle_price, huge_price = 0, 0, 0, 0
    today_price, five_price, twenty_price, sixty_price = 0, 0, 0, 0
    day_list = list()
    inflow_list = InflowStock.objects.filter(Q(is_delete=False) &
                                             Q(shares_hold_id=stock_id)).order_by("-time", "-date")
    for inflow in inflow_list:
        if inflow.date not in day_list:
            price += inflow.main_inflow
            small = inflow.small_inflow
            big = inflow.big_inflow
            middle = inflow.middle_inflow
            huge = inflow.huge_inflow
            day_list.append(inflow.date)
        days = len(set(day_list))
        if days == 1:
            if moment and moment["now"] < moment["inflow_am_time"]:
                today_price = 0
                small_price = 0
                big_price = 0
                middle_price = 0
                huge_price = 0
            else:
                today_price = price
                small_price = small
                big_price = big
                middle_price = middle
                huge_price = huge
            continue
        if today_price == 0:
            if days == 4:
                five_price = price
                continue
            elif days == 19:
                twenty_price = price
                continue
            elif days == 59:
                sixty_price = price
                break
        else:
            if days == 5:
                five_price = price
                continue
            elif days == 20:
                twenty_price = price
                continue
            elif days == 60:
                sixty_price = price
                break

    today_price = round(today_price / 10000) if today_price else 0
    five_price = round(five_price / 10000) if five_price else 0
    twenty_price = round(twenty_price / 10000) if twenty_price else 0
    sixty_price = round(sixty_price / 10000) if sixty_price else 0
    small_price = round(small_price / 10000) if small_price else 0
    big_price = round(big_price / 10000) if big_price else 0
    middle_price = round(middle_price / 10000) if middle_price else 0
    huge_price = round(huge_price / 10000) if huge_price else 0
    text, color = inflow_forecast(small_price, big_price, middle_price, huge_price, today_price)

    data = {
        "main": {
            "main_inflow": today_price,
            "color": font_color(today_price)
        },
        "small": {
            "small_inflow": small_price,
            "color": font_color(small_price)
        },
        "middle": {
            "middle_inflow": middle_price,
            "color": font_color(middle_price)
        },
        "big": {
            "big_inflow": big_price,
            "color": font_color(big_price)
        },
        "huge": {
            "huge_inflow": huge_price,
            "color": font_color(huge_price)
        },
        "five": {
            "five_price": five_price,
            "color": font_color(five_price)
        },
        "twenty": {
            "twenty_price": twenty_price,
            "color": font_color(twenty_price)
        },
        "sixty": {
            "sixty_price": sixty_price,
            "color": font_color(sixty_price)
        },
        "text": [text, color]
    }
    return data


def handle_holder_number_data(stock_id):
    """
    处理股东数量变化数据
    """
    holder_obj = ShareholderNumber.objects.filter(Q(is_delete=False) &
                                                  Q(shares_hold_id=stock_id)).order_by("-end_time").first()

    data = {
        "holder_number": round(holder_obj.holder_number),
        "fluctuate": round(holder_obj.fluctuate, 2),
        "diff_rate": handle_rate(holder_obj.diff_rate),
        "end_time": holder_obj.end_time.strftime("%Y-%m-%d"),
        "avg_amount": handle_price(holder_obj.avg_amount),
        "avg_number": handle_price(holder_obj.avg_number),
        "total_amount": handle_price(holder_obj.total_amount),
        "total_price": handle_price(holder_obj.total_price),
        "notice_date": holder_obj.notice_date.strftime("%Y-%m-%d"),
    } if holder_obj else {}
    return data


def forecast(stock_id: str):
    """
    股票涨跌预测
    """
    hold = SharesHold.objects.get(Q(is_delete=False) & Q(id=stock_id))
    moment = etc_time()
    buy_text, tra_text = "", ""
    if moment["now"] > moment["end_time"]:
        detail = StockDetail.objects.filter(Q(is_delete=False) & Q(shares_hold_id=hold.id)).order_by("-time").first()
        buy_num = detail.buyOne + detail.buyTwo + detail.buyThree + detail.buyFour + detail.buyFive
        sell_num = detail.sellOne + detail.sellTwo + detail.sellThree + detail.sellFour + detail.sellFive
        tra_num = round(detail.traNumber / 10000, 2)
    else:
        quote = ef.stock.get_quote_snapshot(hold.code)
        if quote.empty:
            return buy_text, tra_text
        buy_num = quote["买1数量"] + quote["买2数量"] + quote["买3数量"] + quote["买4数量"] + quote["买5数量"]
        sell_num = quote["卖1数量"] + quote["卖2数量"] + quote["卖3数量"] + quote["卖4数量"] + quote["卖5数量"]
        tra_num = round(quote["成交量"] / 10000, 2)
    diff_num = round(buy_num - sell_num)
    buy_text = f"买入卖出托单差 {diff_num} 手；"
    if diff_num > 0:
        buy_color = "red"
    elif diff_num < 0:
        buy_color = "green"
    else:
        buy_color = ""
    moment = etc_time()
    if moment["now"] >= moment["stock_time"]:
        data_list, labels = handle_tar_number(stock_id)
        if data_list:
            data_list.sort()
            index = data_list.index(tra_num) if tra_num in data_list else 0
            tra_rate = round(index / len(data_list))
            if tra_rate < 0.4:
                tra_text = f"量偏低，在第{index + 1}位；"
            elif 0.4 <= tra_rate <= 0.6:
                tra_text = f"量中等，在第{index + 1}位；"
            else:
                tra_text = f"量偏高，在第{index + 1}位；"
    return [buy_text, buy_color], tra_text
