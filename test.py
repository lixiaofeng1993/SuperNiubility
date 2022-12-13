#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: test.py
# 创建时间: 2022/12/12 0012 20:10
# @Version：V 0.1
# @desc :
import requests


res = requests.get("http://api.mairui.club/hszb/kdj/002047/5m/07d5931508181693cc").json()
print(res)