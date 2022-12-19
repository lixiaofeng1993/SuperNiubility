import efinance as ef
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Q  # 与或非 查询
from django.contrib.auth.decorators import login_required
from django_pandas.io import read_frame

from nb.models import *
from public.auth_token import auth_token
from public.common import *
from public.response import JsonResponse


@method_decorator(login_required, name='dispatch')
class ToDOIndex(ListView):
    """
    签名页面
    """
    model = ToDo
    template_name = 'home/to_do/to_do.html'
    context_object_name = 'object_list'
    paginate_by = NumberOfPages

    def dispatch(self, *args, **kwargs):
        return super(ToDOIndex, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        self.request.session["login_from"] = self.request.get_full_path()
        model = model_superuser(self.request, self.model)
        obj_list = model.filter(is_delete=False).order_by("-create_date")
        obj_list = handle_model(list(obj_list))
        return obj_list

    def get_context_data(self, **kwargs):
        self.page = self.request.GET.dict().get('page', '1')
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        data = pagination_data(paginator, page, is_paginated)
        context.update(data)
        # 列表序号
        flag = (int(self.page) - 1) * self.paginate_by
        # 删除跳转页面
        number = len(self.object_list) % 10
        if number == 1 and len(self.object_list) > 10:
            self.page = int(self.page) - 1
        context.update({'page': self.page, "flag": flag})
        return context


@auth_token()
@login_required
def todo_add(request):
    if request.method == GET:
        return render(request, "home/to_do/add_to_do.html")
    elif request.method == POST:
        body = handle_json(request)
        if not body:
            return JsonResponse.JsonException()
        todo_id = body.get("todo_id")
        describe = body.get("describe")
        end_time = body.get("end_time")
        end_time = end_time if end_time else date.today()
        model = model_superuser(request, ToDo)
        if todo_id:
            if model.filter(Q(describe=describe) & Q(is_delete=False)).exclude(id=todo_id).exists():
                return JsonResponse.RepeatException()
        else:
            if model.filter(Q(describe=describe) & Q(is_delete=False)).exists():
                return JsonResponse.RepeatException()
        try:
            user_id = request.session.get("user_id")
            if todo_id:
                model.filter(id=todo_id).update(describe=describe, end_time=end_time, user_id=user_id)
            else:
                td = ToDo()
                td.describe = describe
                td.end_time = end_time
                td.user_id = user_id
                td.save()
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        todo = model.get(Q(describe=describe) & Q(is_delete=False))
        repr = "待办"
        setattr(todo, "name", describe)
        operation_record(request, todo, todo_id, repr, "")
        return JsonResponse.OK()


@login_required
def todo_edit(request, todo_id):
    if request.method == GET:
        info = request_get_search(request)
        model = model_superuser(request, ToDo)
        td = model.get(id=todo_id)
        data = handle_model(td)
        info.update({"obj": data})
        return render(request, "home/to_do/edit_to_do.html", info)


@login_required
def todo_look(request, todo_id):
    if request.method == GET:
        info = request_get_search(request)
        model = model_superuser(request, ToDo)
        td = model.get(id=todo_id)
        data = handle_model(td)
        info.update({"obj": data})
        return render(request, "home/to_do/look_to_do.html", info)


@auth_token()
def todo_del(request, todo_id):
    if request.method == POST:
        user_id = request.session.get("user_id")
        model = model_superuser(request, ToDo)
        td = model.get(id=todo_id)
        try:
            td.user_id = user_id
            td.save()
            td.delete()
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        repr = "待办"
        setattr(td, "name", td.describe)
        operation_record(request, td, todo_id, repr, "del")
        return JsonResponse.OK()


@method_decorator(login_required, name='dispatch')
class StockIndex(ListView):
    """
    签名页面
    """
    model = SharesHold
    template_name = 'home/stock/stock.html'
    context_object_name = 'object_list'
    paginate_by = NumberOfPages

    def dispatch(self, *args, **kwargs):
        return super(StockIndex, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        self.request.session["login_from"] = self.request.get_full_path()
        model = model_superuser(self.request, self.model)
        obj_list = model.filter(is_delete=False).order_by("-create_date")
        obj_list = handle_model(list(obj_list))
        return obj_list

    def get_context_data(self, **kwargs):
        self.page = self.request.GET.dict().get('page', '1')
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        data = pagination_data(paginator, page, is_paginated)
        context.update(data)
        # 列表序号
        flag = (int(self.page) - 1) * self.paginate_by
        # 删除跳转页面
        number = len(self.object_list) % 10
        if number == 1 and len(self.object_list) > 10:
            self.page = int(self.page) - 1
        context.update({'page': self.page, "flag": flag})
        return context


@auth_token()
def stock_add(request):
    if request.method == GET:
        return render(request, "home/stock/add_stock.html")
    elif request.method == POST:
        body = handle_json(request)
        if not body:
            return JsonResponse.JsonException()
        stock_id = body.get("stock_id")
        name = body.get("name")
        code = body.get("code")
        number = body.get("number")
        cost_price = body.get("cost_price")
        color = body.get("color")
        days = body["days"] if body.get("days") else 1
        is_detail = body["is_detail"] if body.get("is_detail") else False
        model = model_superuser(request, SharesHold)
        if stock_id:
            if model.filter(Q(code=code) & Q(is_delete=False)).exclude(id=stock_id).exists():
                return JsonResponse.RepeatException()
        else:
            hold = model.filter(Q(code=code) & Q(is_delete=False)).exists()
            if hold:
                return JsonResponse.RepeatException()
        moment = etc_time()
        if moment["no_time"] < moment["now"] < moment["start_time"]:
            return JsonResponse.TimeException(message="当前时间禁止添加.")
        code_df = ef.stock.get_quote_history(code, klt=101)
        if code_df.empty:
            return JsonResponse.CheckException(message="股票代码错误.")
        share_name = code_df["股票名称"].values[0]
        if name != share_name:
            return JsonResponse.EqualException(message="名称和代码不相符.")
        try:
            user_id = request.session.get("user_id")
            if stock_id:
                # if is_detail:
                #     hold = model.filter(Q(is_detail=True) & Q(is_delete=False)).first()
                #     if hold:
                #         hold.is_detail = False
                #         hold.save()
                hold = model.filter(Q(id=stock_id) & Q(is_delete=False)).first()
                try:
                    if str(hold.cost_price) != cost_price:
                        change = StockChange()
                        change.name = hold.name
                        change.code = hold.code
                        change.number = hold.number
                        change.cost_price = hold.cost_price
                        change.change_date = moment["now"]
                        change.shares_hold_id = hold.id
                        change.save()
                    model.filter(Q(id=stock_id) & Q(is_delete=False)).update(
                        name=name, code=code, number=number, cost_price=cost_price, color=color, user_id=user_id,
                        is_detail=is_detail, days=days
                    )
                except Exception as error:
                    return JsonResponse.DatabaseException(data=str(error))
            else:
                hold = SharesHold()
                hold.name = name
                hold.code = code
                hold.number = number
                hold.cost_price = cost_price
                hold.color = color
                hold.user_id = user_id
                hold.save()
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        delete_cache(user_id, stock_id)
        hold = model.get(Q(code=code) & Q(is_delete=False))
        repr = "股票"
        operation_record(request, hold, stock_id, repr, "")
        return JsonResponse.OK()


@login_required
def stock_edit(request, stock_id):
    if request.method == GET:
        info = request_get_search(request)
        model = model_superuser(request, SharesHold)
        hold = model.get(id=stock_id)
        data = handle_model(hold)
        info.update({"obj": data})
        return render(request, "home/stock/edit_stock.html", info)


@login_required
def stock_look(request, stock_id):
    info = request_get_search(request)
    model = model_superuser(request, SharesHold)
    hold = model.get(id=stock_id)
    info.update({
        "flag": False,
        "obj": hold,
    })

    def font_color(number):  # 字体颜色
        if number > 0:
            return "red"
        elif number < 0:
            return "green"
        else:
            return "#757575"

    def font_color_two(number, number1):  # 字体颜色
        if number > number1:
            return "red"
        elif number < number1:
            return "green"
        else:
            return "#757575"

    # 股票详情
    detail = StockDetail.objects.filter(Q(is_delete=False) & Q(shares_hold_id=hold.id)).order_by("-time").first()
    if not detail:
        return render(request, "home/stock/look_stock.html", info)
    stock_detail = {
        "todayStartPri": {
            "todayStartPri": detail.todayStartPri,
            "color": font_color_two(detail.todayStartPri, detail.yestodEndPri),
        }, "nowPri": {
            "nowPri": detail.nowPri,
            "color": font_color_two(detail.nowPri, detail.yestodEndPri),
        }, "avg_price": {
            "avg_price": detail.avg_price,
            "color": font_color_two(detail.avg_price, detail.yestodEndPri),
        }, "todayMax": {
            "todayMax": detail.todayMax,
            "color": font_color_two(detail.todayMax, detail.yestodEndPri),
        }, "todayMin": {
            "todayMin": detail.todayMin,
            "color": font_color_two(detail.todayMin, detail.yestodEndPri),
        }, "increPer": {
            "increPer": detail.increPer,
            "color": font_color(detail.increPer),
        }, "increase": {
            "increase": detail.increase,
            "color": font_color(detail.increase),
        },
        "top_price": detail.top_price,
        "down_price": detail.down_price,
        "turnover_rate": detail.turnover_rate,
        "industry": detail.industry,
        "P_E_ratio_dynamic": detail.P_E_ratio_dynamic,
        "ROE_ratio": handle_rate(detail.ROE_ratio),
        "traNumber": handle_price(detail.traNumber),
        "traAmount": handle_price(detail.traAmount),
        "yestodEndPri": detail.yestodEndPri,
        "section_no": detail.section_no,
        "net_profit": handle_price(detail.net_profit),
        "total_market_value": handle_price(detail.total_market_value),
        "circulation_market_value": handle_price(detail.circulation_market_value),
        "gross_profit_margin": handle_rate(detail.gross_profit_margin),
        "net_interest_rate": handle_rate(detail.net_interest_rate),
    }
    # 资金流向
    # 主力资金趋势
    inflow_time_list = InflowStock.objects.filter(Q(is_delete=False) &
                                                  Q(shares_hold_id=hold.id)).exclude(time=None).order_by("-time")
    day_list = list()
    price = 0
    five_price = 0
    twenty_price = 0
    sixty_price = 0
    inflow_date_list = []
    for flow in inflow_time_list:
        day_list.append(flow.date)
    day_list = list(set(day_list))
    i = 0
    for day in day_list:
        _flow = InflowStock.objects.filter(Q(is_delete=False) & Q(date=day) &
                                           Q(shares_hold_id=hold.id)).exclude(time=None).order_by("-time").first()
        price += _flow.main_inflow
        i += 1
        if i == 5:
            five_price = price
            break
        elif i == 20:
            twenty_price = price
            break
        elif i == 60:
            sixty_price = price
            break
    if not sixty_price:
        inflow_date_list = InflowStock.objects.filter(Q(is_delete=False) & Q(time=None) &
                                                      Q(shares_hold_id=hold.id)).order_by("-date")[:60 - len(day_list)]
        for _flow in inflow_date_list:
            sixty_price += _flow.main_inflow
    if not twenty_price:
        for _flow in inflow_date_list[:20 - len(day_list)]:
            twenty_price += _flow.main_inflow
    if not five_price:
        for _flow in inflow_date_list[:5 - len(day_list)]:
            five_price += _flow.main_inflow
    five_price = round((five_price + price) / 10000)
    twenty_price = round((twenty_price + price) / 10000)
    sixty_price = round((sixty_price + price) / 10000)
    if not inflow_time_list and not inflow_date_list:
        return render(request, "home/stock/look_stock.html", info)
    inflow = inflow_time_list[0] if inflow_time_list else inflow_date_list[0]
    # 股票股东
    holder_list = Shareholder.objects.filter(Q(is_delete=False) &
                                             Q(shares_hold_id=hold.id)).order_by("-time", "-hold_rate")[:10]
    for holder in holder_list:
        holder.time = str(holder.time).split(" ")[0]
    # 股票板块
    sector_list = StockSector.objects.filter(Q(is_delete=False) &
                                             Q(shares_hold_id=hold.id)).order_by("-update_date", "-sector_rate")[:20]
    sector_list_diff = list()
    sectors = list()
    for sector in sector_list:
        if sector.sector_name not in sector_list_diff:
            sector.update_date = sector.update_date.strftime("%Y-%m-%d %H:%M")
            sectors.append(sector)
        sector_list_diff.append(sector.sector_name)
    # 龙虎榜
    dragon_obj = StockSuper.objects.filter(Q(is_delete=False) & Q(shares_hold_id=hold.id)).order_by("-time").first()
    # 持仓股东数量数据
    holder_obj = ShareholderNumber.objects.filter(Q(is_delete=False) &
                                                  Q(shares_hold_id=hold.id)).order_by("-end_time").first()

    holder_number = {
        "holder_number": round(holder_obj.holder_number),
        "fluctuate": round(holder_obj.fluctuate, 2),
        "diff_rate": handle_rate(holder_obj.diff_rate),
        "end_time": holder_obj.end_time.strftime("%Y-%m-%d"),
        "avg_amount": handle_price(holder_obj.avg_amount),
        "avg_number": handle_price(holder_obj.avg_number),
        "total_amount": handle_price(holder_obj.total_amount),
        "total_price": handle_price(holder_obj.total_price),
        "notice_date": holder_obj.notice_date.strftime("%Y-%m-%d"),
    } if holder_obj else {}
    info.update({
        "detail": stock_detail,
        "inflow": {
            "main": {
                "main_inflow": round(inflow.main_inflow / 10000),
                "color": font_color(inflow.main_inflow)
            },
            "small": {
                "small_inflow": round(inflow.small_inflow / 10000),
                "color": font_color(inflow.small_inflow)
            },
            "middle": {
                "middle_inflow": round(inflow.middle_inflow / 10000),
                "color": font_color(inflow.middle_inflow)
            },
            "big": {
                "big_inflow": round(inflow.big_inflow / 10000),
                "color": font_color(inflow.big_inflow)
            },
            "huge": {
                "huge_inflow": round(inflow.huge_inflow / 10000),
                "color": font_color(inflow.huge_inflow)
            },
            "five": {
                "five_price": five_price,
                "color": font_color(five_price)
            },
            "twenty": {
                "twenty_price": twenty_price,
                "color": font_color(twenty_price)
            },
            "sixty": {
                "sixty_price": sixty_price,
                "color": font_color(sixty_price)
            },
        },
        "holder": holder_list,
        "dragon_obj": dragon_obj,
        "holder_number": holder_number,
        "sector": sectors,
        "update_time": format_time(detail.time),
    })
    Message.objects.filter(Q(is_delete=False) & Q(is_look=False) &
                           Q(obj_id=stock_id) & Q(type=Detail)).update(is_look=True)
    return render(request, "home/stock/look_stock.html", info)


@login_required
def chart_look(request, stock_id):
    if request.method == GET:
        info = request_get_search(request)
        model = model_superuser(request, SharesHold)
        hold = model.get(id=stock_id)
        shares = Shares.objects.filter(Q(is_delete=False) & Q(shares_hold_id=stock_id)).order_by("-update_date").first()
        if not shares:
            return render(request, "home/stock/chart_stock.html", info)
        info.update({
            "obj": hold,
            "update_time": format_time(shares.update_date),
            "flag": hold.cost_price
        })
        Message.objects.filter(Q(is_delete=False) & Q(is_look=False) &
                               Q(obj_id=stock_id) & Q(type=Chart)).update(is_look=True)
        return render(request, "home/stock/chart_stock.html", info)


@login_required
def chart_all(request):
    if request.method == GET:
        info = request_get_search(request)
        model = model_superuser(request, SharesHold)
        hold = model.filter(is_delete=False).order_by("-update_date").first()
        info.update({
            "obj": hold,
            "update_time": format_time(hold.update_date),
        })
        Message.objects.filter(Q(is_delete=False) & Q(is_look=False)).update(is_look=True)
        return render(request, "home/stock/chart_all.html", info)


@login_required
def dragon(request):
    if request.method == GET:
        info = request_get_search(request)
        moment = check_stoke_date()
        last_day = None
        if moment:
            last_day = moment["today"]
        else:
            stock = StockSuper.objects.filter(is_delete=False).order_by("-time").first()
            if stock:
                last_day = stock.time
        stock_list = StockSuper.objects.filter(Q(is_delete=False) & Q(time=last_day)).order_by("open_price")
        for stock in stock_list:
            stock.name = stock.name + "\n" + stock.code
            stock.time = stock.time.strftime("%Y-%m-%d")
            stock.rise_rate = handle_rate(stock.rise_rate)
            stock.net_purchase_amount = handle_price(stock.net_purchase_amount)
            stock.purchase_amount = handle_price(stock.purchase_amount)
            stock.sales_amount = handle_price(stock.sales_amount)
            stock.turnover_amount = handle_price(stock.turnover_amount)
            stock.total_turnover_amount = handle_price(stock.total_turnover_amount)
            stock.net_purchases_rate = handle_rate(stock.net_purchases_rate)
            stock.net_turnover_rate = handle_rate(stock.net_turnover_rate)
            stock.market_equity = handle_price(stock.market_equity)
            stock.turnover_rate = handle_rate(stock.turnover_rate)
        info.update({
            "stock_list": stock_list
        })
        Message.objects.filter(Q(is_delete=False) & Q(is_look=False) & Q(type=Dragon)).update(is_look=True)
        return render(request, "home/stock/dragon.html", info)


@auth_token()
def stock_del(request, stock_id):
    if request.method == POST:
        user_id = request.session.get("user_id")
        model = model_superuser(request, SharesHold)
        hold = model.get(id=stock_id)
        share = Shares.objects.filter(shares_hold_id=stock_id)
        try:
            hold.user_id = user_id
            hold.save()
            share.delete()
            hold.delete()
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        delete_cache(user_id, stock_id)
        repr = "股票"
        operation_record(request, hold, stock_id, repr, "del")
        return JsonResponse.OK()


@method_decorator(login_required, name='dispatch')
class RecordIndex(ListView):
    """
    操作记录页面
    """
    model = LogEntry
    template_name = 'home/record/record.html'
    context_object_name = 'object_list'
    paginate_by = NumberOfPages

    def dispatch(self, *args, **kwargs):
        return super(RecordIndex, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        self.request.session["login_from"] = self.request.get_full_path()
        obj_list = self.model.objects.all().order_by("-action_time")
        obj_list = handle_model(list(obj_list))
        return obj_list

    def get_context_data(self, **kwargs):
        self.page = self.request.GET.dict().get('page', '1')
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        data = pagination_data(paginator, page, is_paginated)
        context.update(data)
        # 列表序号
        flag = (int(self.page) - 1) * self.paginate_by
        # 删除跳转页面
        number = len(self.object_list) % 10
        if number == 1 and len(self.object_list) > 10:
            self.page = int(self.page) - 1
        context.update({'page': self.page, "flag": flag})
        return context


@login_required
def record_look(request, record_id):
    info = request_get_search(request)
    log = LogEntry.objects.get(id=record_id)
    info.update({"obj": log})
    repr = "记录"
    operation_record(request, log, log.change_message, repr, "change")
    return render(request, "home/record/look_record.html", info)
