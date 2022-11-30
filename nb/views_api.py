#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: views_api.py
# 创建时间: 2022/11/20 0020 11:13
# @Version：V 0.1
# @desc :
from django.forms.models import model_to_dict
from django.db.models import Q  # 与或非 查询
from dateutil.relativedelta import relativedelta

from .tasks import stock_history, last_day_stock_history
from nb.models import ToDo, SharesHold, Shares, StockDetail
from public.auth_token import auth_token
from public.common import *
from public.response import JsonResponse


def recommend_poetry(request):
    if request.method == POST:
        user_id = request.session.get("user_id")
        obj_list = home_poetry(user_id)
        return JsonResponse.OK(data=obj_list)


@auth_token()
def poetry_detail(request, poetry_id):
    if request.method == POST:
        user_id = request.session.get("user_id")
        result = cache.get(PoetryDetail.format(user_id=user_id, poetry_id=poetry_id))
        if result:
            return JsonResponse.OK(data=result)
        poetry = Poetry.objects.get(id=poetry_id)
        result = model_to_dict(handle_model(poetry))
        introduce = poetry.author.introduce.split("►")[0] if poetry.author.introduce else ""
        result.update({
            "author": poetry.author.name,
            "dynasty": poetry.author.dynasty,
            "introduce": introduce,
        })
        cache.set(PoetryDetail.format(user_id=user_id, poetry_id=poetry_id), result, surplus_second())
        repr = "诗词"
        msg = f"查看{repr}《{poetry.name}》"
        operation_record(request, poetry, poetry.id, repr, "", msg)
        return JsonResponse.OK(data=result)


@auth_token()
def todo_done(request, todo_id):
    if request.method == POST:
        body = handle_json(request)
        if not body:
            return JsonResponse.JsonException()
        model = model_superuser(request, ToDo)
        td = model.get(id=todo_id)
        flag = body.get("flag")
        moment = etc_time()
        end_time = td.end_time.strftime("%Y-%m-%d")
        today = str(moment["today"])
        if end_time < today and not td.is_done:
            return JsonResponse.CheckException(message="此待办已过期，无法修改状态.")
        try:
            if flag:
                td.is_done = 0
            else:
                td.is_done = 1
            td.save()
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        repr = "待办"
        msg = f"修改{repr} {td.describe} 未完成" if flag else f"修改{repr} {td.describe} 已完成"
        operation_record(request, td, td.id, repr, "", msg)
        return JsonResponse.OK()


@auth_token()
def todo_home(request, todo_id):
    if request.method == POST:
        model = model_superuser(request, ToDo)
        td = model.get(id=todo_id)
        if td.is_done == 0:
            return JsonResponse.BadRequest()
        try:
            td.is_home = True
            td.save()
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        repr = "待办"
        msg = f"修改{repr} {td.describe} 不在首页展示"
        operation_record(request, td, td.id, repr, "", msg)
        return JsonResponse.OK()


@auth_token()
def todo_find_number(request, number):
    if request.method == POST:
        model = model_superuser(request, ToDo)
        try:
            todo_list = model.filter(Q(is_delete=False) &
                                     Q(is_home=False) &
                                     (Q(is_done=0) | Q(is_done=1)) &
                                     Q(end_time=date.today())).order_by("-create_date")[:number]
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        todo_list = handle_model(list(todo_list.values()))
        return JsonResponse.OK(data=todo_list)


@auth_token()
def stock_import(request, hold_id):
    if request.method == POST:
        model = model_superuser(request, SharesHold)
        hold = model.get(id=hold_id)
        code = hold.code
        user_id = hold.user_id
        moment = etc_time()
        if moment["now"] >= moment["end_time"]:
            end = moment["now"].strftime("%Y%m%d")
        else:
            end = (moment["now"] + relativedelta(days=-1)).strftime("%Y%m%d")
        start = (moment["now"] + relativedelta(months=-6)).strftime("%Y%m%d")
        share = Shares.objects.filter(Q(code=code) & Q(shares_hold_id=hold_id)).exists()
        if share:
            return JsonResponse.RepeatException()
        flag = True
        last_day_time = ""
        if not check_stoke_date() or moment["now"] >= moment["end_time"]:
            flag = False
            last_day_stock_history.delay(code=code, hold_id=hold_id, user_id=user_id)
            while 1:
                end_time = cache.get(StockEndTime.format(user_id=user_id))
                if not end_time:
                    time.sleep(5)
                break
        if not flag:
            share = Shares.objects.filter(Q(code=code) & Q(shares_hold_id=hold_id)).first()
            date_time = datetime.strptime(share.date_time, "%Y-%m-%d %H:%M")
            last_day_time = share.date_time.split(" ")[0]
            end = (date_time + relativedelta(days=-1)).strftime("%Y%m%d")
        stock_history.delay(
            code=code, hold_id=hold_id, user_id=user_id, beg=start, end=end, last_day_time=last_day_time
        )
        repr = "股票"
        msg = f"导入 {hold.name} 历史数据"
        operation_record(request, hold, hold.id, repr, "", msg)
        return JsonResponse.OK()


@auth_token()
def day_chart(request):
    if request.method == POST:
        user_id = request.session.get("user_id")
        datasets = cache.get(TodayChart.format(user_id=user_id))
        if datasets:
            return JsonResponse.OK(data=datasets)
        model = model_superuser(request, SharesHold)
        hold_list = model.filter(is_delete=False)
        datasets = dict()
        moment = etc_time()
        for hold in hold_list:
            if check_stoke_day():  # 休市日展示最后一天的数据
                last_day = str(moment["today"])
            else:
                if hold.last_day:
                    last_day = str(hold.last_day).split(" ")[0]
                else:
                    share_first = Shares.objects.filter(
                        Q(shares_hold_id=hold.id) & Q(is_delete=False)).order_by("-date_time").first()
                    if not share_first:
                        continue
                    last_day = share_first.date_time.split(" ")[0]
            share_list = Shares.objects.filter(
                Q(shares_hold_id=hold.id) & Q(is_delete=False) &
                Q(date_time__contains=last_day)).order_by("date_time")
            if not share_list:
                continue
            share_list = handle_model(list(share_list))
            labels = list()
            data_list = list()
            for share in share_list:
                labels.append(share.date_time)
                data_list.append(share.new_price)
            datasets.update({
                hold.name: {
                    "data": data_list,
                    "color": hold.color,
                },
                "labels": labels

            })
        cache.set(TodayChart.format(user_id=user_id), datasets, 3 * 60)
        return JsonResponse.OK(data=datasets)


@auth_token()
def five_chart(request):
    if request.method == POST:
        user_id = request.session.get("user_id")
        datasets = cache.get(FiveChart.format(user_id=user_id))
        if datasets:
            return JsonResponse.OK(data=datasets)
        model = model_superuser(request, SharesHold)
        hold_list = model.filter(is_delete=False)
        datasets = dict()
        moment = etc_time()
        for hold in hold_list:
            share_list = Shares.objects.filter(
                Q(shares_hold_id=hold.id) &
                Q(is_delete=False)).exclude(date_time__contains=str(moment["today"])).order_by("-date_time")
            if not share_list:
                continue
            share_list = handle_model(list(share_list))
            labels = list()
            data_list = list()
            day_list = list()
            for share in share_list:
                if len((set(day_list))) > 5:
                    labels.pop()
                    data_list.pop()
                    break
                date_time = share.date_time
                day_flag = date_time.split(" ")[0]
                day_list.append(day_flag)
                flag = date_time.split(":")[-1]
                if flag in StockRule:
                    labels.append(share.date_time)
                    data_list.append(share.new_price)
            data_list = list(reversed(data_list))
            labels = list(reversed(labels))
            datasets.update({
                hold.name: {
                    "data": data_list,
                    "color": hold.color,
                },
                "labels": labels,
                "days": len((set(day_list))) - 1

            })
        cache.set(FiveChart.format(user_id=user_id), datasets, surplus_second())
        return JsonResponse.OK(data=datasets)


@auth_token()
def ten_chart(request):
    if request.method == POST:
        user_id = request.session.get("user_id")
        datasets = cache.get(TenChart.format(user_id=user_id))
        if datasets:
            return JsonResponse.OK(data=datasets)
        model = model_superuser(request, SharesHold)
        hold_list = model.filter(is_delete=False)
        datasets = dict()
        moment = etc_time()
        for hold in hold_list:
            share_list = Shares.objects.filter(
                Q(shares_hold_id=hold.id) &
                Q(is_delete=False)).exclude(date_time__contains=str(moment["today"])).order_by("-date_time")
            if not share_list:
                continue
            share_list = handle_model(list(share_list))
            labels = list()
            data_list = list()
            day_list = list()
            for share in share_list:
                if len((set(day_list))) > 10:
                    labels.pop()
                    data_list.pop()
                    break
                date_time = share.date_time
                day_flag = date_time.split(" ")[0]
                day_list.append(day_flag)
                flag = date_time.split(":")[-1]
                if flag in StockRule:
                    labels.append(share.date_time)
                    data_list.append(share.new_price)
            data_list = list(reversed(data_list))
            labels = list(reversed(labels))
            datasets.update({
                hold.name: {
                    "data": data_list,
                    "color": hold.color,
                },
                "labels": labels,
                "days": len((set(day_list))) - 1

            })
        cache.set(TenChart.format(user_id=user_id), datasets, surplus_second())
        return JsonResponse.OK(data=datasets)


@auth_token()
def twenty_chart(request):
    if request.method == POST:
        user_id = request.session.get("user_id")
        datasets = cache.get(TwentyChart.format(user_id=user_id))
        if datasets:
            return JsonResponse.OK(data=datasets)
        model = model_superuser(request, SharesHold)
        hold_list = model.filter(is_delete=False)
        datasets = dict()
        moment = etc_time()
        for hold in hold_list:
            share_list = Shares.objects.filter(
                Q(shares_hold_id=hold.id) &
                Q(is_delete=False)).exclude(date_time__contains=str(moment["today"])).order_by("-date_time")
            if not share_list:
                continue
            share_list = handle_model(list(share_list))
            labels = list()
            data_list = list()
            day_list = list()
            for share in share_list:
                if len((set(day_list))) > 20:
                    labels.pop()
                    data_list.pop()
                    break
                date_time = share.date_time
                day_flag = date_time.split(" ")[0]
                day_list.append(day_flag)
                flag = date_time.split(":")[-1]
                if flag in StockRule:
                    labels.append(share.date_time)
                    data_list.append(share.new_price)
            data_list = list(reversed(data_list))
            labels = list(reversed(labels))
            datasets.update({
                hold.name: {
                    "data": data_list,
                    "color": hold.color,
                },
                "labels": labels,
                "days": len((set(day_list))) - 1

            })
        cache.set(TwentyChart.format(user_id=user_id), datasets, surplus_second())
        return JsonResponse.OK(data=datasets)


@auth_token()
def half_year_chart(request):
    if request.method == POST:
        user_id = request.session.get("user_id")
        datasets = cache.get(YearChart.format(user_id=user_id))
        if datasets:
            return JsonResponse.OK(data=datasets)
        model = model_superuser(request, SharesHold)
        hold_list = model.filter(is_delete=False)
        datasets = dict()
        moment = etc_time()
        for hold in hold_list:
            share_list = Shares.objects.filter(
                Q(shares_hold_id=hold.id) &
                Q(is_delete=False)).exclude(date_time__contains=str(moment["today"])).order_by("date_time")
            if not share_list:
                continue
            share_list = handle_model(list(share_list))
            labels = list()
            data_list = list()
            day_list = list()
            for share in share_list:
                date_time = share.date_time
                day_flag = date_time.split(" ")[0]
                day_list.append(day_flag)
                flag = date_time.split(":")[-1]
                if flag in StockRule:
                    labels.append(share.date_time)
                    data_list.append(share.new_price)
            datasets.update({
                hold.name: {
                    "data": data_list,
                    "color": hold.color,
                },
                "labels": labels,
                "days": len((set(day_list)))

            })
        cache.set(YearChart.format(user_id=user_id), datasets, surplus_second())
        return JsonResponse.OK(data=datasets)


@auth_token()
def buy_sell_chart(request):
    if request.method == POST:
        user_id = request.session.get("user_id")
        datasets = cache.get(TodayBuySellChart.format(user_id=user_id))
        if datasets:
            return JsonResponse.OK(data=datasets)
        model = model_superuser(request, SharesHold)
        hold = model.filter(Q(is_delete=False) & Q(is_detail=True)).first()
        if not hold:
            return JsonResponse.Emptyeption()
        moment = etc_time()
        if check_stoke_day():  # 休市日展示最后一天的数据
            last_day = moment["today"]
        else:
            if hold.last_day:
                last_day = hold.last_day
            else:
                share_first = StockDetail.objects.filter(
                    Q(shares_hold_id=hold.id) & Q(is_delete=False)).order_by("-time").first()
                if not share_first:
                    return JsonResponse.OK()
                last_day = share_first.date
        detail_list = StockDetail.objects.filter(
            Q(shares_hold_id=hold.id) & Q(is_delete=False) & Q(date=last_day)).order_by("time")
        if not detail_list:
            return JsonResponse.OK()
        detail_list = handle_model(list(detail_list))
        labels = list()
        buy_one_list = list()
        buy_two_list = list()
        buy_three_list = list()
        buy_four_list = list()
        buy_five_list = list()
        sell_one_list = list()
        sell_two_list = list()
        sell_three_list = list()
        sell_four_list = list()
        sell_five_list = list()
        for detail in detail_list:
            buy_one_list.append(detail.buyOne)
            buy_two_list.append(detail.buyTwo)
            buy_three_list.append(detail.buyThree)
            buy_four_list.append(detail.buyFour)
            buy_five_list.append(detail.buyFive)
            sell_one_list.append(detail.sellOne)
            sell_two_list.append(detail.sellTwo)
            sell_three_list.append(detail.sellThree)
            sell_four_list.append(detail.sellFour)
            sell_five_list.append(detail.sellFive)
            labels.append(detail.time)
        datasets = {
            "labels": labels,
            "datasets": [
                {
                    "label": "买一",
                    "data": buy_one_list,
                    "borderColor": "red",
                    "backgroundColor": "red",
                    "stack": "1",
                }, {
                    "label": "买二",
                    "data": buy_two_list,
                    "borderColor": 'red',
                    "backgroundColor": 'red',
                    "stack": "1",
                }, {
                    "label": "买三",
                    "data": buy_three_list,
                    "borderColor": 'red',
                    "backgroundColor": 'red',
                    "stack": "1",
                }, {
                    "label": "买四",
                    "data": buy_four_list,
                    "borderColor": 'red',
                    "backgroundColor": 'red',
                    "stack": "1",
                }, {
                    "label": "买五",
                    "data": buy_five_list,
                    "borderColor": 'red',
                    "backgroundColor": 'red',
                    "stack": "1",
                }, {
                    "label": "卖一",
                    "data": sell_one_list,
                    "borderColor": 'green',
                    "backgroundColor": 'green',
                    "stack": "2",
                },
                {
                    "label": "卖二",
                    "data": sell_two_list,
                    "borderColor": 'green',
                    "backgroundColor": 'green',
                    "stack": "2",
                }, {
                    "label": "卖三",
                    "data": sell_three_list,
                    "borderColor": 'green',
                    "backgroundColor": 'green',
                    "stack": "2",
                }, {
                    "label": "卖四",
                    "data": sell_four_list,
                    "borderColor": 'green',
                    "backgroundColor": 'green',
                    "stack": "2",
                }, {
                    "label": "卖五",
                    "data": sell_five_list,
                    "borderColor": 'green',
                    "backgroundColor": 'green',
                    "stack": "2",
                },
            ]
        }
        cache.set(TodayBuySellChart.format(user_id=user_id), datasets, 3 * 60)
        return JsonResponse.OK(data=datasets)


@auth_token()
def record(request):
    if request.method == POST:
        log_list = LogEntry.objects.all().order_by("-action_time")[:5]
        data_list = list()
        for log in log_list:
            log_dict = model_to_dict(log)
            log_dict["format_time"] = format_time(log.action_time)
            data_list.append(log_dict)
        log_list = handle_model(data_list)
        return JsonResponse.OK(data=log_list)
