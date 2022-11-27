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


def handle_body():
    body = {
        "msgtype": "markdown",
        "markdown": {
            "title": share_name,
            "text": f"### {share_name}\n\n"
                    f"> **历史 {so_day} 天最高价** <font color={max_price_color}>{max_price}</font> 元/股\n\n"

        },
        "at": {
            "atMobiles": ["15235514553"],
            "isAtAll": False,
        }}
