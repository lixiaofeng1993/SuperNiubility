from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.db.models import Q  # 与或非 查询
from dateutil.relativedelta import relativedelta
import efinance as ef

from .tasks import stock_history
from nb.models import ToDo, SharesHold, Shares
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
        obj_list = self.model.objects.filter(is_delete=False).order_by("-create_date")
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
        if number == 1:
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
        if todo_id:
            if ToDo.objects.filter(describe=describe).exclude(id=todo_id).exists():
                return JsonResponse.RepeatException()
        else:
            if ToDo.objects.filter(describe=describe).exists():
                return JsonResponse.RepeatException()
        try:
            if todo_id:
                ToDo.objects.filter(id=todo_id).update(describe=describe, end_time=end_time)
            else:
                td = ToDo()
                td.describe = describe
                td.end_time = end_time
                td.save()
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        return JsonResponse.OK()


@login_required
def todo_edit(request, todo_id):
    if request.method == GET:
        info = request_get_search(request)
        td = ToDo.objects.get(id=todo_id)
        data = handle_model(td)
        info.update({"obj": data})
        return render(request, "home/to_do/edit_to_do.html", info)


@auth_token()
def todo_del(request, todo_id):
    if request.method == POST:
        td = ToDo.objects.get(id=todo_id)
        try:
            td.delete()
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        return JsonResponse.OK()


@auth_token()
def todo_done(request, todo_id):
    if request.method == POST:
        body = handle_json(request)
        if not body:
            return JsonResponse.JsonException()
        flag = body.get("flag")
        td = ToDo.objects.get(id=todo_id)
        try:
            if flag:
                td.is_done = 0
            else:
                td.is_done = 1
            td.save()
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        return JsonResponse.OK()


@auth_token()
def todo_home(request, todo_id):
    if request.method == POST:
        td = ToDo.objects.get(id=todo_id)
        if td.is_done == 0:
            return JsonResponse.BadRequest()
        try:
            td.is_home = True
            td.save()
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        return JsonResponse.OK()


@auth_token()
def todo_find_number(request, number):
    if request.method == POST:
        try:
            todo_list = ToDo.objects.filter(Q(is_delete=False) &
                                            Q(is_home=False) &
                                            (Q(is_done=0) | Q(is_done=1)) &
                                            Q(end_time=date.today())).order_by("-create_date")[:number]
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        todo_list = handle_model(list(todo_list.values()))
        return JsonResponse.OK(data=todo_list)


@method_decorator(login_required, name='dispatch')
class StockIndex(ListView):
    """
    签名页面
    """
    model = SharesHold
    template_name = 'home/stock/stock.html'
    context_object_name = 'object_list'
    paginate_by = NumberOfPages / 5

    def dispatch(self, *args, **kwargs):
        return super(StockIndex, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        obj_list = self.model.objects.filter(is_delete=False).order_by("-create_date")
        moment = etc_time()
        for obj in obj_list:
            setattr(obj, "days", (moment["now"] - obj.create_date).days + 1)  # 持仓天数
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
        if stock_id:
            if SharesHold.objects.filter(Q(code=code) & Q(is_delete=False)).exclude(id=stock_id).exists():
                return JsonResponse.RepeatException()
        else:
            hold = SharesHold.objects.filter(Q(code=code) & Q(is_delete=False)).exists()
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
            if stock_id:
                SharesHold.objects.filter(Q(id=stock_id) & Q(is_delete=False)).update(
                    name=name, code=code, number=number, cost_price=cost_price, color=color
                )
            else:
                hold = SharesHold()
                hold.name = name
                hold.code = code
                hold.number = number
                hold.cost_price = cost_price
                hold.color = color
                hold.save()
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        delete_cache()
        return JsonResponse.OK()


@login_required
def stock_edit(request, stock_id):
    if request.method == GET:
        info = request_get_search(request)
        hold = SharesHold.objects.get(id=stock_id)
        data = handle_model(hold)
        info.update({"obj": data})
        return render(request, "home/stock/edit_stock.html", info)


@auth_token()
def stock_del(request, stock_id):
    if request.method == POST:
        hold = SharesHold.objects.get(id=stock_id)
        share = Shares.objects.filter(shares_hold_id=stock_id)
        try:
            share.delete()
            hold.delete()
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        delete_cache()
        return JsonResponse.OK()


@auth_token()
def stock_import(request, hold_id):
    if request.method == POST:
        hold = SharesHold.objects.get(id=hold_id)
        code = hold.code
        hold_id = hold.id
        moment = etc_time()
        if moment["now"] >= moment["end_time"]:
            end = moment["now"].strftime("%Y%m%d")
        else:
            end = (moment["now"] + relativedelta(days=-1)).strftime("%Y%m%d")
        start = (moment["now"] + relativedelta(months=-6)).strftime("%Y%m%d")
        share = Shares.objects.filter(code=code)
        if share:
            return JsonResponse.RepeatException()
        stock_history.delay(code=code, hold_id=hold_id, beg=start, end=end)
        return JsonResponse.OK()


@auth_token()
def half_year_chart(request):
    if request.method == POST:
        datasets = cache.get(YearChart)
        if datasets:
            return JsonResponse.OK(data=datasets)
        hold_list = SharesHold.objects.filter(is_delete=False)
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
                if flag in ["00", "15", "30", "45"]:
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
        cache.set(YearChart, datasets, surplus_second())
        return JsonResponse.OK(data=datasets)


@auth_token()
def day_chart(request):
    if request.method == POST:
        hold_list = SharesHold.objects.filter(is_delete=False)
        datasets = dict()
        moment = etc_time()
        for hold in hold_list:
            if check_stoke_day():
                share_list = Shares.objects.filter(
                    Q(shares_hold_id=hold.id) & Q(is_delete=False) &
                    Q(date_time__contains=str(moment["today"]))).order_by("date_time")
            else:
                last_day = (moment["now"] + relativedelta(days=-1)).strftime("%Y-%m-%d")
                share_list = Shares.objects.filter(
                    Q(shares_hold_id=hold.id) & Q(is_delete=False) &
                    Q(date_time__contains=last_day)).order_by("date_time")
            if len(share_list) != 240:
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
        return JsonResponse.OK(data=datasets)


@auth_token()
def five_chart(request):
    if request.method == POST:
        datasets = cache.get(FiveChart)
        if datasets:
            return JsonResponse.OK(data=datasets)
        hold_list = SharesHold.objects.filter(is_delete=False)
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
                if flag in ["00", "15", "30", "45"]:
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
        cache.set(FiveChart, datasets, surplus_second())
        return JsonResponse.OK(data=datasets)


@auth_token()
def ten_chart(request):
    if request.method == POST:
        datasets = cache.get(TenChart)
        if datasets:
            return JsonResponse.OK(data=datasets)
        hold_list = SharesHold.objects.filter(is_delete=False)
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
                if flag in ["00", "15", "30", "45"]:
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
        cache.set(TenChart, datasets, surplus_second())
        return JsonResponse.OK(data=datasets)
