#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: views_com.py
# 创建时间: 2022/12/25 0025 11:45
# @Version：V 0.1
# @desc :
import efinance as ef

from nb.models import InflowStock, ShareholderNumber
from public.common import *


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
