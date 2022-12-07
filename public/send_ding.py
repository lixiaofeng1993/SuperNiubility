#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: send_ding.py
# 创建时间: 2022/11/27 0027 14:57
# @Version：V 0.1
# @desc :
import hmac
import urllib.parse
import hashlib
import base64
import requests
import urllib3
import time
from public.log import logger

urllib3.disable_warnings()


def ding_sign():
    """
    发送钉钉消息加密
    :return:
    """
    timestamp = str(round(time.time() * 1000))
    secret = "SEC4abe8f6887a15a96ff1e8358e8ee0602025a0cb2f73a4c46c1105cbe9424250c"
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign


def send_ding(body: dict):
    """
    发送钉钉消息
    :param body
    :return:
    """
    headers = {"Content-Type": "application/json"}
    access_token = "dfb892d96c26718f34f10fb494b463e28fb41049250a9a15f5fd8ebc50e7d1ca"
    timestamp, sign = ding_sign()

    res = requests.post(
        "https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}".format(
            access_token, timestamp, sign), headers=headers, json=body, verify=False).json()
    if res["errcode"] == 0 and res["errmsg"] == "ok":
        logger.info("钉钉通知发送成功！info：{}".format(body["markdown"]["text"]))
    else:
        logger.error("钉钉通知发送失败！返回值：{}".format(res))


def profit_and_loss(hold):
    """
    盈亏转换发送钉钉文档
    """
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
                    f"> **{profit_text}：** <font color={color}>{hold.profit_and_loss}</font> 元\n\n"
                    f"> **点击查看** [股票分析](http://121.41.54.234/nb/stock/look/{hold.id}/)@15235514553"
        },
        "at": {
            "atMobiles": ["15235514553"],
            "isAtAll": False,
        }}
    send_ding(body)


def profit_and_loss_ratio(hold, price):
    """
    盈亏比例
    """
    ratio = round((float(price) - hold.cost_price) / hold.cost_price * 100, 3)
    if -5 < ratio < 5:
        pass
    else:
        if ratio > 0:
            color = "#FF0000"
            text = "盈利"
        else:
            color = "#00FF00"
            text = "亏损"
        body = {
            "msgtype": "markdown",
            "markdown": {
                "title": hold.name,
                "text": f"### {hold.name}\n\n"
                        f"> **盈亏比例：** {text} 已经达到 <font color={color}>{ratio}</font> %\n\n"
                        f"> **点击查看** [股票分析](http://121.41.54.234/nb/stock/look/{hold.id}/)@15235514553"
            },
            "at": {
                "atMobiles": ["15235514553"],
                "isAtAll": False,
            }}
        send_ding(body)
