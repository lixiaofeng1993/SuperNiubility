#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: views_api.py
# 创建时间: 2022/11/20 0020 11:13
# @Version：V 0.1
# @desc :
from django.forms.models import model_to_dict
from dateutil.relativedelta import relativedelta
from django_pandas.io import read_frame

from .tasks import stock_history, last_day_stock_history
from nb.models import ToDo, Shares, StockDetail, InflowStock
from public.auth_token import auth_token
from public.common import *
from public.response import JsonResponse


def recommend_poetry(request):
    if request.method == POST:
        obj_list = cache.get(RECOMMEND)
        if not obj_list:
            obj_list = home_poetry()
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
        datasets, user_id, stock_id = handle_cache(request, "day")
        if isinstance(datasets, dict):
            return JsonResponse.OK(data=datasets)
        dataset = dict()
        moment = etc_time()
        for hold in datasets:
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
            dataset.update({
                hold.name: {
                    "data": data_list,
                    "color": hold.color,
                },
                "labels": labels

            })
        logger.info("查询当天股票k线成功.")
        if stock_id:
            cache.set(TodayStockChart.format(stock_id=stock_id), dataset, surplus_second())
        else:
            cache.set(TodayChart.format(user_id=user_id), dataset, surplus_second())
        return JsonResponse.OK(data=dataset)


@auth_token()
def five_chart(request):
    if request.method == POST:
        datasets, user_id, stock_id = handle_cache(request, "five")
        if isinstance(datasets, dict):
            return JsonResponse.OK(data=datasets)
        dataset = dict()
        moment = etc_time()
        for hold in datasets:
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
            dataset.update({
                hold.name: {
                    "data": data_list,
                    "color": hold.color,
                },
                "labels": labels,
                "days": len((set(day_list))) - 1

            })
        logger.info("查询5天股票k线成功.")
        if stock_id:
            cache.set(FiveStockChart.format(stock_id=stock_id), dataset, surplus_second())
        else:
            cache.set(FiveChart.format(user_id=user_id), dataset, surplus_second())
        return JsonResponse.OK(data=dataset)


@auth_token()
def ten_chart(request):
    if request.method == POST:
        datasets, user_id, stock_id = handle_cache(request, "ten")
        if isinstance(datasets, dict):
            return JsonResponse.OK(data=datasets)
        dataset = dict()
        moment = etc_time()
        for hold in datasets:
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
            dataset.update({
                hold.name: {
                    "data": data_list,
                    "color": hold.color,
                },
                "labels": labels,
                "days": len((set(day_list))) - 1

            })
        logger.info("查询10天股票k线成功.")
        if stock_id:
            cache.set(TenStockChart.format(stock_id=stock_id), dataset, surplus_second())
        else:
            cache.set(TenChart.format(user_id=user_id), dataset, surplus_second())
        return JsonResponse.OK(data=dataset)


@auth_token()
def twenty_chart(request):
    if request.method == POST:
        datasets, user_id, stock_id = handle_cache(request, "twenty")
        if isinstance(datasets, dict):
            return JsonResponse.OK(data=datasets)
        dataset = dict()
        moment = etc_time()
        for hold in datasets:
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
            dataset.update({
                hold.name: {
                    "data": data_list,
                    "color": hold.color,
                },
                "labels": labels,
                "days": len((set(day_list))) - 1

            })
        logger.info("查询20天股票k线成功.")
        if stock_id:
            cache.set(TwentyStockChart.format(stock_id=stock_id), dataset, surplus_second())
        else:
            cache.set(TwentyChart.format(user_id=user_id), dataset, surplus_second())
        return JsonResponse.OK(data=dataset)


@auth_token()
def half_year_chart(request):
    if request.method == POST:
        datasets, user_id, stock_id = handle_cache(request, "year")
        if isinstance(datasets, dict):
            return JsonResponse.OK(data=datasets)
        dataset = dict()
        moment = etc_time()
        diff = dict()
        for hold in datasets:
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
            number = diff.get("number")  # 多个股票，数据不一致的问题
            days = diff.get("days")
            if number and number <= len(labels):
                pass
            if days and days <= len(set(day_list)):
                pass
            else:
                diff["number"] = len(labels)
                diff["days"] = len(set(day_list))
            number = diff.get("number")
            days = diff.get("days")
            dataset.update({
                hold.name: {
                    "data": data_list[-number:],
                    "color": hold.color,
                },
                "labels": labels[-number:],
                "days": days

            })
        logger.info("查询全部股票k线成功.")
        if stock_id:
            cache.set(YearStockChart.format(stock_id=stock_id), dataset, surplus_second())
        else:
            cache.set(YearChart.format(user_id=user_id), dataset, surplus_second())
        return JsonResponse.OK(data=dataset)


@auth_token()
def buy_sell_chart(request):
    if request.method == POST:
        datasets, user_id, stock_id = handle_cache(request, "buy")
        if isinstance(datasets, dict):
            return JsonResponse.OK(data=datasets)
        if not stock_id:
            return JsonResponse.CheckException()
        hold = datasets[0]
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
            "name": hold.name,
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
        logger.info(f"查询 {hold.name} 当天买入卖出托单股票数据成功.")
        cache.set(TodayBuySellChart.format(stock_id=stock_id), datasets, surplus_second())
        return JsonResponse.OK(data=datasets)


@auth_token()
def inflow_chart(request):
    if request.method == POST:
        datasets, user_id, stock_id = handle_cache(request, "inflow")
        if isinstance(datasets, dict):
            return JsonResponse.OK(data=datasets)
        if not stock_id:
            return JsonResponse.CheckException()
        hold = datasets[0]
        moment = etc_time()
        if check_stoke_day():  # 休市日展示最后一天的数据
            last_day = moment["today"]
        else:
            if hold.last_day:
                last_day = hold.last_day
            else:
                share_first = InflowStock.objects.filter(
                    Q(shares_hold_id=hold.id) & Q(is_delete=False)).order_by("-time").first()
                if not share_first:
                    return JsonResponse.OK()
                last_day = share_first.date
        detail_list = InflowStock.objects.filter(
            Q(shares_hold_id=hold.id) & Q(is_delete=False) & Q(date=last_day)).order_by("time")
        if not detail_list:
            return JsonResponse.OK()
        detail_list = handle_model(list(detail_list))
        labels = list()
        main_list = list()
        small_list = list()
        middle_list = list()
        big_list = list()
        huge_list = list()
        flag = "00"
        for detail in detail_list:
            date_time = detail.time
            if not date_time:
                continue
            flag = date_time.split(":")[-2]
            if flag in StockRule:
                main_list.append(round(detail.main_inflow / 10000))
                small_list.append(round(detail.small_inflow / 10000))
                middle_list.append(round(detail.middle_inflow / 10000))
                big_list.append(round(detail.big_inflow / 10000))
                huge_list.append(round(detail.huge_inflow / 10000))
                labels.append(detail.time)
        if flag not in StockRule:
            main_list.append(round(detail_list[-1].main_inflow / 10000))
            small_list.append(round(detail_list[-1].small_inflow / 10000))
            middle_list.append(round(detail_list[-1].middle_inflow / 10000))
            big_list.append(round(detail_list[-1].big_inflow / 10000))
            huge_list.append(round(detail_list[-1].huge_inflow / 10000))
            labels.append(detail_list[-1].time)
        datasets = {
            "labels": labels,
            "name": hold.name,
            "datasets": [
                {
                    "label": "主力净流入",
                    "data": main_list,
                    "borderColor": "red",
                    "backgroundColor": "#880000",
                    "stack": "1",
                }, {
                    "label": "小单净流入",
                    "data": small_list,
                    "borderColor": 'red',
                    "backgroundColor": '#00FFFF',
                    "stack": "2",
                }, {
                    "label": "中单净流入",
                    "data": middle_list,
                    "borderColor": 'red',
                    "backgroundColor": '#008080',
                    "stack": "3",
                }, {
                    "label": "大单净流入",
                    "data": big_list,
                    "borderColor": 'red',
                    "backgroundColor": '#808000',
                    "stack": "4",
                }, {
                    "label": "超大单净流入",
                    "data": huge_list,
                    "borderColor": 'red',
                    "backgroundColor": '#000080',
                    "stack": "5",
                }
            ]
        }
        logger.info(f"查询 {hold.name} 当天资金流入流出股票数据成功.")
        cache.set(TodayInflowChart.format(stock_id=stock_id), datasets, surplus_second())
        return JsonResponse.OK(data=datasets)


@auth_token()
def record(request):
    if request.method == POST:
        log_list = LogEntry.objects.all().order_by("-action_time")[:HomeNumber]
        data_list = list()
        for log in log_list:
            log_dict = model_to_dict(log)
            log_dict["format_time"] = format_time(log.action_time)
            data_list.append(log_dict)
        log_list = handle_model(data_list)
        return JsonResponse.OK(data=log_list)


@auth_token()
def message_remind(request):
    if request.method == POST:
        # moment = etc_time()
        # & Q(date=moment["today"])
        message_list = Message.objects.filter(Q(is_delete=False) &
                                              Q(is_look=False)).order_by("-create_date")
        flag = True
        if not message_list:
            flag = False
            message_list = Message.objects.filter(Q(is_delete=False) &
                                                  Q(is_look=True)).order_by("-create_date")
        result = {
            "number": len(message_list),
            "flag": flag,
            "data": [],
        }
        if not message_list:
            return JsonResponse.OK(data=result)
        for message in message_list[:HomeNumber]:
            result["data"].append({
                "now_time": format_time(message.create_date),
                "obj_id": message.obj_id,
                "name": message.name,
                "type": message.type,
            })
        return JsonResponse.OK(data=result)
