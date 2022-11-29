#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: views_api_v1.py
# 创建时间: 2022/11/29 0029 20:04
# @Version：V 0.1
# @desc :
from faker import Faker

from public.conf import GET
from public.response import JsonResponse


def get_faker(request, number: int = 1):
    if request.method == GET:
        faker = Faker("zh-CN")
        number = 1 if number < 1 else number
        data = faker.profile()
        del data["current_location"]
        del data["birthdate"]
        if number == 1:
            data["phone"] = faker.phone_number()
            data["card"] = faker.credit_card_number()
        else:
            del data["job"]
            del data["residence"]
            del data["website"]
            data["phone"] = []
            data["card"] = []
            data["ssn"] = []
            data["address"] = []
            data["mail"] = []
            for i in range(number):
                data["phone"].append(faker.phone_number())
                data["card"].append(faker.credit_card_number())
                data["address"].append(faker.address())
                data["ssn"].append(faker.ssn())
                data["mail"].append(faker.email())
        return JsonResponse.OK(data=data)
