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

from public.conf import *
from public.log import logger


def delete_cache():
    """
    清除redis缓存
    """
    cache.delete(YearChart)
    cache.delete(FiveChart)
    cache.delete(TenChart)


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
        "no_time": datetime(year, month, day, 9, 0, 0),
        "start_time": datetime(year, month, day, 9, 25, 0),
        "end_time": datetime(year, month, day, 15, 5, 0),
        "ap_time": datetime(year, month, day, 11, 35, 0),
        "pm_time": datetime(year, month, day, 13, 00, 0),
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
    moment = etc_time()
    weekday = date(moment["year"], moment["month"], moment["day"]).strftime("%A")
    if not is_workday(date(moment["year"], moment["month"], moment["day"])) or weekday in ["Saturday", "Sunday"]:
        logger.info(f"当前时间 {moment['today']} 休市日!!!")
        return
    return moment


def check_stoke_date():
    moment = check_stoke_day()
    if not moment:
        return
    if moment["now"] < moment["start_time"] or moment["now"] > moment["end_time"] or \
            moment["ap_time"] < moment["now"] < moment["pm_time"]:
        logger.info(f"当前时间 {moment['now']} 未开盘!!!")
        return
    return True


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


def format_obj(obj: object):
    if hasattr(obj, "end_time"):
        obj.end_time = str(obj.end_time).split(" ")[0]
    if obj.update_date:
        obj.update_date = obj.update_date.strftime("%Y-%m-%d %H:%M:%S")
    if obj.create_date:
        obj.create_date = obj.create_date.strftime("%Y-%m-%d %H:%M:%S")
    if hasattr(obj, "is_delete"):
        obj.is_delete = "false"
    if hasattr(obj, "id"):
        obj.id = str(obj.id)
    return obj


def handle_model(model_obj):
    """
    end_time 时间格式化
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
            else:
                obj = format_obj(obj)
            model_obj.append(obj)
    else:
        model_obj = format_obj(model_obj)
    return model_obj


def request_get_search(request) -> dict:
    """
    封装获取get请求公共参数
    :param request:
    :return:
    """
    search_name = request.GET.get('search-input', '')
    page = request.GET.get('page', '1')
    info = {
        'search_name': search_name,
        'page': page
    }
    return info


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
