#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: sensitive.py
# 创建时间: 2022/11/27 0027 15:53
# @Version：V 0.1
# @desc :

from public.conf import SensitiveList


def sensitive_words(text: str = ""):
    for msg in SensitiveList:
        text = text.replace(msg, "*" * len(msg))
    return text
