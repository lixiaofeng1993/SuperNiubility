#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: stock_api.py
# 创建时间: 2022/11/28 0028 18:48
# @Version：V 0.1
# @desc :

import requests

from public.conf import STOCK_KEY, KDJ_KEY
from public.log import logger


def stock_api(code: str):
    """
    股票详细数据
    code sz002047
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "gid": f"{code}",
        "key": STOCK_KEY,
    }
    try:
        res = requests.get("http://web.juhe.cn:8080/finance/stock/hs", headers=headers, params=data,
                           verify=False).json()
        error_code = res.get("error_code")
        if error_code == 10012:
            logger.error(f"沪深股市api 请求超过次数限制 ===>>> {res['reason']} ===>>> {res['error_code']}")
            return
        elif error_code != 0:
            logger.error(f"沪深股市api 出现异常 ===>>> {res['reason']} ===>>> {res['error_code']}")
            return
        resultcode = res.get("resultcode")
        if resultcode == "200":
            return res["result"][0]
    except Exception as error:
        logger.error(f"沪深股市api 请求出现异常 ===>>> {error}")
        return


def kdj_api(level: str, code: str):
    url = f"http://api.mairui.club/hszb/kdj/{code}/{level}/{KDJ_KEY}"
    try:
        response = requests.get(url, verify=False).json()
    except Exception as error:
        logger.error(f"kdj接口请求报错 ===>>> {error}")
        return
    return response


if __name__ == '__main__':
    print(kdj_api("5m", "002047"))
