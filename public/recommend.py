#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: recommend.py
# 创建时间: 2022/11/20 0020 11:16
# @Version：V 0.1
# @desc :
import requests
import time
from datetime import date
from jsonpath import jsonpath
from random import randint

from public.conf import CALENDAR_KEY, POETRY_TYPE, WEATHER_KEY, CITY_NAME
from public.log import logger


def get_holiday(msg: str = ""):
    if not msg:
        now = date.today()
        day = str(int(now.year)) + "-" + str(int(now.month)) + "-" + str(int(now.day))
    else:
        day = msg
    # res = requests.get(f"http://v.juhe.cn/calendar/day?date={day}&key={CALENDAR_KEY}").json()
    # if res["error_code"] == 10012:
    #     logger.error(f"获取当天的详细信息接口 请求超过次数限制 ===>>> {res['reason']} ===>>> {res['error_code']}")
    #     return
    # elif res["error_code"] != 0:
    #     logger.error(f"获取当天的详细信息接口出现异常 ===>>> {res['reason']} ===>>> {res['error_code']}")
    #     return
    # holiday = res["result"]["data"]["holiday"]
    holiday = ""
    return holiday


def get_weather():
    """
    获取天气 晴，多云等
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {
        "key": WEATHER_KEY,
        "city": CITY_NAME
    }
    # res = requests.get("http://apis.juhe.cn/simpleWeather/query", headers=headers, params=params, verify=False).json()
    # if res["error_code"] == 10012:
    #     logger.error(f"根据城市查询天气接口 请求超过次数限制 ===>>> {res['reason']} ===>>> {res['error_code']}")
    #     return
    # elif res["error_code"] != 0:
    #     logger.error(f"根据城市查询天气接口出现异常 ===>>> {res['reason']} ===>>> {res['error_code']}")
    #     return
    # weather = jsonpath(res, "$.result.realtime.info")
    # weather = weather[0] if weather else ""
    weather = "沙"
    return weather


def now_season():
    """
    立春 2月3-5日
    立夏 5月05-07日
    立秋 8月7或9日
    立冬 11月7-8日
    """
    season = ""
    year = date.today().year
    month = date.today().month
    day = date.today().day
    if month in [3, 4]:
        season = "春天"
    elif month in [6, 7]:
        season = "夏天"
    elif month in [9, 10]:
        season = "秋天"
    elif month in [12, 1]:
        season = "冬天"
    elif month == 2:
        value = 3
        for i in [3, 4, 5]:
            msg = f"{year}-2-{i}"
            msg_data = get_holiday(msg=msg)
            if msg_data == "立春":
                value = i
                break
        season = "春天" if day >= value else "冬天"
    elif month == 5:
        value = 5
        for i in [5, 6, 7]:
            msg = f"{year}-5-{i}"
            msg_data = get_holiday(msg=msg)
            if msg_data == "立夏":
                value = i
                break
        season = "夏天" if day >= value else "春天"
    elif month == 8:
        value = 7
        for i in [7, 8, 9]:
            msg = f"{year}-8-{i}"
            msg_data = get_holiday(msg=msg)
            if msg_data == "立秋":
                value = i
                break
        season = "秋天" if day >= value else "夏天"
    elif month == 11:
        value = 7
        for i in [7, 8]:
            msg = f"{year}-11-{i}"
            msg_data = get_holiday(msg=msg)
            if msg_data == "立冬":
                value = i
                break
        season = "冬天" if day >= value else "秋天"
    return season


def recommend_handle():
    holiday = get_holiday()
    if holiday and holiday in POETRY_TYPE.keys():
        poetry_type = holiday
    else:
        weather = get_weather()
        type_list = list()
        if weather:
            if "晴" in weather:
                type_list = ["爱情", "友情"]
            elif "雨" in weather:
                type_list = ["写雨", "思乡", "离别", "伤感"]
            elif "风" in weather:
                type_list = ["写风"]
            elif "雪" in weather:
                type_list = ["写雪", "梅花"]
            elif "云" in weather:
                type_list = ["写云"]
            elif "沙" in weather or "霾" in weather:
                type_list = ["边塞"]
        type_list.append(now_season())
        poetry_type = type_list[randint(0, len(type_list) - 1)]
    return poetry_type


def surplus_second():
    today = date.today()
    today_end = f"{str(today)} 23:59:59"
    end_second = int(time.mktime(time.strptime(today_end, "%Y-%m-%d %H:%M:%S")))
    now_second = int(time.time())
    return end_second - now_second


if __name__ == '__main__':
    print(recommend_handle())
