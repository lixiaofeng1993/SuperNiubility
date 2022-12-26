#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: common.py
# 创建时间: 2022/11/21 0021 17:42
# @Version：V 0.1
# @desc :

import json
import time
from django.core.cache import cache
from chinese_calendar import is_workday
from random import randint, choice
from django.db.models import Q  # 与或非 查询
from django.contrib.admin.models import LogEntry, CHANGE, ADDITION, DELETION
from django.contrib.admin.options import get_content_type_for_model

from nb.models import Poetry, Message, SharesHold, StockDetail
from public.send_ding import profit_and_loss, profit_and_loss_ratio, limit_up
from public.conf import *
from public.recommend import recommend_handle
from public.log import logger


def random_str():
    """
    随机字符串
    """
    H = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    salt = ""
    for i in range(CodeNumber):
        salt += choice(H)
    return salt


def difference_stock(code: str):
    """
    区分沪深市场
    """
    # 沪市股票包含上证主板和科创板和B股：沪市主板股票代码是60开头、科创板股票代码是688开头、B股代码900开头
    if code.startswith("60") or code.startswith("688") or code.startswith("900"):
        return f"sh{code}"
    # 深市股票包含主板、中小板、创业板和B股：深市主板股票代码是000开头、中小板股票代码002开头、创业板300开头、B股代码200开头
    elif code.startswith("000") or code.startswith("002") or code.startswith("300") or code.startswith("200"):
        return f"sz{code}"


def delete_cache(user_id, stock_id):
    """
    清除redis缓存
    """
    cache.delete(YearChart.format(user_id=user_id))
    cache.delete(YearStockChart.format(stock_id=stock_id))
    cache.delete(FiveChart.format(user_id=user_id))
    cache.delete(FiveStockChart.format(stock_id=stock_id))
    cache.delete(TenChart.format(user_id=user_id))
    cache.delete(TenStockChart.format(stock_id=stock_id))
    cache.delete(TodayChart.format(user_id=user_id))
    cache.delete(TodayStockChart.format(stock_id=stock_id))
    cache.delete(TodayBuySellChart.format(stock_id=stock_id))
    cache.delete(TodayKDJChart.format(user_id=user_id))
    cache.delete(TwentyChart.format(user_id=user_id))
    cache.delete(TwentyStockChart.format(stock_id=stock_id))
    cache.delete(TodayInflowChart.format(stock_id=stock_id))
    cache.delete(TodayCostPrice.format(stock_id=stock_id))


def regularly_hold(hold, moment: dict, price: float, old_price: float):
    """
    实时更新 持有股票收益
    """
    is_profit = hold.is_profit = True if hold.profit_and_loss > 0 else False
    hold.profit_and_loss = round(hold.number * float(price) - hold.number * hold.cost_price, 2)
    hold.today_price = round((float(price) - old_price) * hold.number, 2)
    if hold.cost_price:
        profit_and_loss_ratio(hold, price)
        if moment["now"] >= moment["stock_time"]:
            hold.last_close_price = price
            hold.last_day = moment["today"]
            hold.days += 1
    try:
        hold.save()
        logger.info(f"实时更新 持有股票 {hold.name} 收益 保存成功！")
        return is_profit
    except Exception as error:
        logger.error(f"实时更新 持有股票收益 保存报错！===>>> {error}")


def format_time(date_time: datetime):
    """
    格式化时间天，小时，分钟，秒
    """
    now = etc_time()["now"]
    total_seconds = round((now - date_time).total_seconds())
    total_seconds = total_seconds if total_seconds > 0 else 1
    if total_seconds < 60:
        _time = f"{total_seconds}秒前"
    elif 60 <= total_seconds < 3600:
        _time = f"{round(total_seconds / 60)}分钟前"
    elif 3600 <= total_seconds < 86400:
        _time = f"{round(total_seconds / 3600)}小时前"
    elif 86400 <= total_seconds < 172800:
        _time = f"{round(total_seconds / 86400)}天前"
    else:
        _time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    return _time


def etc_time():
    """
    日期字典
    """
    # 当前日期
    today = date.today()  # 2022-11-25
    # 当前年、月、日
    year, month, day = today.year, today.month, today.day
    moment = {
        "today": today,
        "now": datetime.now(),
        "year": today.year,
        "month": today.month,
        "day": today.day,
        "no_time": datetime(year, month, day, 9, 0, 0),  # 禁止添加时间
        "start_time": datetime(year, month, day, 9, 15, 0),  # 定时任务开始时间
        "end_time": datetime(year, month, day, 15, 10, 0),  # 定时任务结束时间
        "stock_time": datetime(year, month, day, 15, 0, 0),  # 股市停止时间
        "ap_time": datetime(year, month, day, 11, 40, 00),  # 股市上午停止时间
        "pm_time": datetime(year, month, day, 13, 0, 0),  # 股市下午开始时间
        "stock_am_time": datetime(year, month, day, 9, 30, 0),  # 股市开始时间
        "today_end_time": datetime(year, month, day, 23, 59, 59),  # 股市开始时间
    }
    return moment


def surplus_second():
    """
    当天剩余秒数
    """
    today = date.today()
    today_end = f"{str(today)} 23:59:59"
    end_second = int(time.mktime(time.strptime(today_end, "%Y-%m-%d %H:%M:%S")))
    now_second = int(time.time())
    return end_second - now_second


def check_stoke_day():
    """
    是否休市日
    """
    moment = etc_time()
    weekday = date(moment["year"], moment["month"], moment["day"]).strftime("%A")
    if not is_workday(date(moment["year"], moment["month"], moment["day"])) or weekday in ["Saturday", "Sunday"]:
        logger.info(f"当前时间 {moment['today']} 休市日!!!")
        return
    return moment


def check_stoke_date():
    """
    是否开盘
    """
    moment = check_stoke_day()
    if not moment:
        return
    if moment["now"] < moment["start_time"] or moment["now"] > moment["end_time"] or \
            moment["ap_time"] < moment["now"] < moment["pm_time"]:
        logger.info(f"当前时间 {moment['now']} 未开盘!!!")
        return
    return moment


def handle_json(request):
    """
    转化js json传参为dict
    """
    try:
        body = request.body.decode()
        body_dict = json.loads(body)
        return body_dict
    except json.JSONDecodeError as error:
        return


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


def format_obj(obj: object):
    if hasattr(obj, "end_time"):
        obj.end_time = str(obj.end_time).split(" ")[0]
    if hasattr(obj, "update_date"):
        obj.update_date = obj.update_date.strftime("%Y-%m-%d %H:%M:%S")
    if hasattr(obj, "create_date"):
        obj.create_date = obj.create_date.strftime("%Y-%m-%d %H:%M:%S")
    if hasattr(obj, "is_delete"):
        obj.is_delete = "false"
    if hasattr(obj, "id"):
        obj.id = str(obj.id)
    if hasattr(obj, "action_time"):
        obj.action_time = obj.action_time.strftime("%Y-%m-%d %H:%M:%S")
    if hasattr(obj, "time") and obj.time:
        obj.time = obj.time.strftime("%Y-%m-%d %H:%M:%S")
    return obj


def handle_model(model_obj):
    """
    数据库 时间字段 格式化
    """
    if isinstance(model_obj, list):
        obj_list = model_obj.copy()
        model_obj = []
        for obj in obj_list:
            if isinstance(obj, dict):
                if "end_time" in obj.keys():
                    obj["end_time"] = str(obj["end_time"]).split(" ")[0]
                if "update_date" in obj.keys():
                    obj["update_date"] = obj["update_date"].strftime("%Y-%m-%d %H:%M:%S")
                if "create_date" in obj.keys():
                    obj["create_date"] = obj["create_date"].strftime("%Y-%m-%d %H:%M:%S")
                if "is_delete" in obj.keys():
                    obj["is_delete"] = "false"
                if "id" in obj.keys():
                    obj["id"] = str(obj["id"])
                if "action_time" in obj.keys():
                    obj["action_time"] = obj["action_time"].strftime("%Y-%m-%d %H:%M:%S")
                if "time" in obj.keys():
                    obj["time"] = obj["time"].strftime("%Y-%m-%d %H:%M:%S")
            else:
                obj = format_obj(obj)
            model_obj.append(obj)
    elif isinstance(model_obj, object):
        model_obj = format_obj(model_obj)
    return model_obj


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


def model_superuser(request, model):
    """
    用户权限
    超级管理员可以看所有，普通用户只能看自己的数据
    """
    is_super = request.session.get("super")
    if is_super:
        return model.objects
    else:
        user_id = request.session.get("user_id")
        return model.objects.filter(user_id=user_id)


def request_get_search(request) -> dict:
    """
    封装获取get请求公共参数
    :param request:
    :return:
    """
    request.session["login_from"] = request.get_full_path()
    search_name = request.GET.get('search-input', '')
    page = request.GET.get('page', '1')
    info = {
        'search_name': search_name,
        'page': page
    }
    return info


def handle_cache(request, flag: str):
    """
    判断缓存和查询数据
    """
    body = handle_json(request)
    stock_id, datasets = None, None
    if body:
        stock_id = body.get("stock_id")
    user_id = request.session.get("user_id")
    if stock_id:
        if flag == "day":
            datasets = cache.get(TodayStockChart.format(stock_id=stock_id))
        elif flag == "five":
            datasets = cache.get(FiveStockChart.format(stock_id=stock_id))
        elif flag == "ten":
            datasets = cache.get(TenStockChart.format(stock_id=stock_id))
        elif flag == "twenty":
            datasets = cache.get(TwentyStockChart.format(stock_id=stock_id))
        elif flag == "year":
            datasets = cache.get(YearStockChart.format(stock_id=stock_id))
        elif flag == "buy":
            datasets = cache.get(TodayBuySellChart.format(stock_id=stock_id))
        elif flag == "inflow":
            datasets = cache.get(TodayInflowChart.format(stock_id=stock_id))
        elif flag == "price":
            datasets = cache.get(TodayPrice.format(stock_id=stock_id))
        elif flag == "cost":
            datasets = cache.get(TodayCostPrice.format(stock_id=stock_id))
        elif flag == "number":
            datasets = cache.get(TodayTraNumber.format(stock_id=stock_id))
    else:
        if flag == "day":
            datasets = cache.get(TodayChart.format(user_id=user_id))
        elif flag == "five":
            datasets = cache.get(FiveChart.format(user_id=user_id))
        elif flag == "ten":
            datasets = cache.get(TenChart.format(user_id=user_id))
        elif flag == "twenty":
            datasets = cache.get(TwentyChart.format(user_id=user_id))
        elif flag == "year":
            datasets = cache.get(YearChart.format(user_id=user_id))
        elif flag == "kdj":
            datasets = cache.get(TodayKDJChart.format(user_id=user_id))
    if datasets:
        return datasets, user_id, stock_id
    model = model_superuser(request, SharesHold)
    if stock_id:
        hold_list = model.filter(Q(is_delete=False) & Q(id=stock_id))
    else:
        hold_list = model.filter(is_delete=False)
    return hold_list, user_id, stock_id


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


def handle_price(price):
    """
    数据加单位
    """
    if price >= 100000000 or price <= -100000000:
        price = str(round(price / 100000000, 2)) + "亿"
    elif price >= 10000 or price <= -10000:
        price = str(round(price / 10000, 2)) + "万"
    else:
        price = round(price, 2)
    return price


def handle_rate(rate):
    """
    数据加 %
    """
    return str(round(rate, 2)) + "%"


def font_color(number):  # 字体颜色
    """
    根据0判断展示字体颜色
    """
    if number > 0:
        return "red"
    elif number < 0:
        return "green"
    else:
        return "#757575"


def font_color_two(number, number1):  # 字体颜色
    """
    两个数据比较判断字体颜色
    """
    if number > number1:
        return "red"
    elif number < number1:
        return "green"
    else:
        return "#757575"


def pagination_data(paginator, page, is_paginated):
    """
    牛掰的分页
    :param paginator:
    :param page:
    :param is_paginated:
    :return:
    """
    if not is_paginated:
        # 如果没有分页，则无需显示分页导航条，不用任何分页导航条的数据，因此返回一个空的字典
        return {}

    # 当前页左边连续的页码号，初始值为空
    left = []

    # 当前页右边连续的页码号，初始值为空
    right = []

    # 标示第 1 页页码后是否需要显示省略号
    left_has_more = False

    # 标示最后一页页码前是否需要显示省略号
    right_has_more = False

    # 标示是否需要显示第 1 页的页码号。
    # 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
    # 其它情况下第一页的页码是始终需要显示的。
    # 初始值为 False
    first = False

    # 标示是否需要显示最后一页的页码号。
    # 需要此指示变量的理由和上面相同。
    last = False

    # 获得用户当前请求的页码号
    page_number = page.number

    # 获得分页后的总页数
    total_pages = paginator.num_pages

    # 获得整个分页页码列表，比如分了四页，那么就是 [1, 2, 3, 4]
    page_range = paginator.page_range

    if page_number == 1:
        # 如果用户请求的是第一页的数据，那么当前页左边的不需要数据，因此 left=[]（已默认为空）。
        # 此时只要获取当前页右边的连续页码号，
        # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 right = [2, 3]。
        # 注意这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
        right = page_range[page_number:page_number + 2]

        # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
        # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
        if right[-1] < total_pages - 1:
            right_has_more = True

        # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
        # 所以需要显示最后一页的页码号，通过 last 来指示
        if right[-1] < total_pages:
            last = True

    elif page_number == total_pages:
        # 如果用户请求的是最后一页的数据，那么当前页右边就不需要数据，因此 right=[]（已默认为空），
        # 此时只要获取当前页左边的连续页码号。
        # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 left = [2, 3]
        # 这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
        left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]

        # 如果最左边的页码号比第 2 页页码号还大，
        # 说明最左边的页码号和第 1 页的页码号之间还有其它页码，因此需要显示省略号，通过 left_has_more 来指示。
        if left[0] > 2:
            left_has_more = True

        # 如果最左边的页码号比第 1 页的页码号大，说明当前页左边的连续页码号中不包含第一页的页码，
        # 所以需要显示第一页的页码号，通过 first 来指示
        if left[0] > 1:
            first = True
    else:
        # 用户请求的既不是最后一页，也不是第 1 页，则需要获取当前页左右两边的连续页码号，
        # 这里只获取了当前页码前后连续两个页码，你可以更改这个数字以获取更多页码。
        left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
        right = page_range[page_number:page_number + 2]

        # 是否需要显示最后一页和最后一页前的省略号
        if right[-1] < total_pages - 1:
            right_has_more = True
        if right[-1] < total_pages:
            last = True

        # 是否需要显示第 1 页和第 1 页后的省略号
        if left[0] > 2:
            left_has_more = True
        if left[0] > 1:
            first = True

    data = {
        "left": left,
        "right": right,
        "left_has_more": left_has_more,
        "right_has_more": right_has_more,
        "first": first,
        "last": last,
    }

    return data
