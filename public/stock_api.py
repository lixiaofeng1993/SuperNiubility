#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: stock_api.py
# 创建时间: 2022/11/28 0028 18:48
# @Version：V 0.1
# @desc :

import requests

from public.conf import STOCK_KEY
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


if __name__ == '__main__':
    # print(stock_api("sz002047"))
    data = {
        'buyFive': '361200',
        'buyFivePri': '4.160',
        'buyFour': '281400',
        'buyFourPri': '4.170',
        'buyOne': '361900',
        'buyOnePri': '4.200',
        'buyThree': '332900',
        'buyThreePri': '4.180',
        'buyTwo': '130700',
        'buyTwoPri': '4.190',
        'competitivePri': '4.200',
        'date': '2022-11-28',
        'gid': 'sz002047',
        'increPer': '-2.33',
        'increase': '-0.10',
        'name': '宝鹰股份',
        'nowPri': '4.200',
        'reservePri': '4.210',
        'sellFive': '285700',
        'sellFivePri': '4.250',
        'sellFour': '186900',
        'sellFourPri': '4.240',
        'sellOne': '192500',
        'sellOnePri': '4.210',
        'sellThree': '259900',
        'sellThreePri': '4.230',
        'sellTwo': '192600',
        'sellTwoPri': '4.220',
        'time': '15:00:00',
        'todayMax': '4.260',
        'todayMin': '4.170',
        'todayStartPri': '4.250',
        'traAmount': '105176513.300',
        'traNumber': '249966',
        'yestodEndPri': '4.300'
    }
    date_time = f'{data["date"]} {data["time"]}'
    print(date_time)