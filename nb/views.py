from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView
# from django.db.models import Q  # 与或非 查询
from django.contrib.auth.decorators import login_required
# from django_pandas.io import read_frame

from nb.models import *
from nb.tasks import real_time_stock
from public.auth_token import auth_token
from public.views_com import *
from public.response import JsonResponse


@method_decorator(login_required, name='dispatch')
class ToDOIndex(ListView):
    """
    待办任务页面
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
    股票页面
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
        obj_list = model.filter(is_delete=False).order_by("-number", "-create_date")
        obj_list = handle_model(list(obj_list))
        return stock_home(obj_list)

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
                hold = model.filter(Q(id=stock_id) & Q(is_delete=False)).first()
                try:
                    if str(hold.cost_price) != cost_price:  # 持仓成本修改后，更新 StockChange 表
                        change = StockChange()
                        change.name = hold.name
                        change.code = hold.code
                        change.number = hold.number
                        change.cost_price = cost_price
                        change.change_date = moment["now"]
                        change.shares_hold_id = hold.id
                        change.save()
                        real_time_stock.delay(stock_id=hold.id)  # 更新持仓成本后，实时刷新盈亏
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
    hold = model.filter(Q(id=stock_id) & Q(is_delete=False)).first()
    info.update({
        "obj": hold,
    })
    update_time = None
    # 股票详情
    detail = handle_detail_data(stock_id)
    # 资金流向
    # 主力资金趋势
    inflow = handle_inflow_data(stock_id)
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
            update_time = sector.create_date
            sector.update_date = sector.update_date.strftime("%Y-%m-%d %H:%M")
            sectors.append(sector)
        sector_list_diff.append(sector.sector_name)
    # 龙虎榜
    dragon_obj = StockSuper.objects.filter(Q(is_delete=False) & Q(shares_hold_id=hold.id)).order_by("-time").first()
    # 持仓股东数量数据
    number = handle_holder_number_data(stock_id)
    # 预测
    text = inflow.get("text")
    buy_text, tra_text = forecast(stock_id)
    info.update({
        "detail": detail,
        "inflow": inflow,
        "holder": holder_list,
        "dragon_obj": dragon_obj,
        "holder_number": number,
        "sector": sectors,
        "text": {
            "inflow": {
                "text": text[0],
                "color": text[1],
            }, "buy": {
                "text": buy_text[0],
                "color": buy_text[1],
            }, "tra": tra_text
        },
        "update_time": format_time(update_time),
    })
    Message.objects.filter(Q(is_delete=False) & Q(is_look=False) &
                           Q(obj_id=stock_id) & Q(type=Detail)).update(is_look=True)
    return render(request, "home/stock/look_stock.html", info)


@login_required
def chart_look(request, stock_id):
    """
    单个股票图表
    """
    if request.method == GET:
        info = request_get_search(request)
        model = model_superuser(request, SharesHold)
        hold = model.get(id=stock_id)
        info.update({
            "obj": hold,
            "flag": hold.cost_price
        })
        shares = Shares.objects.filter(Q(is_delete=False) & Q(shares_hold_id=stock_id)).order_by("-update_date").first()
        if not shares:
            return render(request, "home/stock/chart_stock.html", info)
        info.update({
            "update_time": format_time(shares.update_date),
        })
        Message.objects.filter(Q(is_delete=False) & Q(is_look=False) &
                               Q(obj_id=stock_id) & Q(type=Chart)).update(is_look=True)
        return render(request, "home/stock/chart_stock.html", info)


@login_required
def chart_all(request):
    """
    所有股票图表
    """
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
    """
    龙虎榜
    """
    if request.method == GET:
        info = request_get_search(request)
        stock = StockSuper.objects.filter(is_delete=False).order_by("-time").first()
        if not stock:
            return render(request, "home/stock/dragon.html", info)
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
    """
    查看操作记录
    """
    info = request_get_search(request)
    log = LogEntry.objects.get(id=record_id)
    info.update({"obj": log})
    repr = "记录"
    operation_record(request, log, log.change_message, repr, "change")
    return render(request, "home/record/look_record.html", info)
