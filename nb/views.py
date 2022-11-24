from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.db.models import Q  # 与或非 查询
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import efinance as ef

from .tasks import stock_history, stock_today
from nb.models import ToDo, SharesHold, Shares
from public.conf import GET, POST, NumberOfPages
from public.auth_token import auth_token
from public.common import handle_json, pagination_data, handle_model, request_get_search
from public.response import JsonResponse
from public.log import logger


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
            if ToDo.objects.filter(describe=describe).exclude(id=todo_id):
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
    paginate_by = NumberOfPages / 2

    def dispatch(self, *args, **kwargs):
        return super(StockIndex, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        obj_list = self.model.objects.filter(is_delete=False).order_by("-create_date")
        today = datetime.now()
        for obj in obj_list:
            setattr(obj, "days", (today - obj.create_date).days + 1)  # 持仓天数
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
def stock_add(request):
    if request.method == GET:
        return render(request, "home/stock/add_stock.html")
    elif request.method == POST:
        body = handle_json(request)
        if not body:
            return JsonResponse.JsonException()
        name = body.get("name")
        code = body.get("code")
        number = body.get("number")
        cost_price = body.get("cost_price")
        color = body.get("color")
        hold = SharesHold.objects.filter(Q(name=name) | Q(code=code)).exists()
        if hold:
            return JsonResponse.RepeatException()
        name_df = ef.stock.get_quote_history(name, klt=101)
        if name_df.empty:
            return JsonResponse.CheckException(message="股票名称错误.")
        share_name = name_df["股票名称"].values[0]
        code_df = ef.stock.get_quote_history(code, klt=101)
        if code_df.empty:
            return JsonResponse.CheckException(message="股票代码错误.")
        code_name = code_df["股票名称"].values[0]
        if share_name != code_name:
            return JsonResponse.EqualException(message="名称和代码不相符.")
        try:
            hold = SharesHold()
            hold.name = name
            hold.code = code
            hold.number = number
            hold.cost_price = cost_price
            hold.color = color
            hold.save()
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        return JsonResponse.OK()


@auth_token()
def stock_import(request, hold_id):
    if request.method == POST:
        hold = SharesHold.objects.get(id=hold_id)
        name = hold.name
        hold_id = hold.id
        end = (datetime.now() + relativedelta(days=-1)).strftime("%Y%m%d")
        start = (datetime.now() + relativedelta(months=-6)).strftime("%Y%m%d")
        share = Shares.objects.filter(name=name)
        if share:
            return JsonResponse.RepeatException()
        stock_history.delay(name=name, hold_id=hold_id, beg=start, end=end)
        return JsonResponse.OK()


@auth_token()
def half_year_chart(request):
    if request.method == POST:
        hold_list = SharesHold.objects.filter(is_delete=False)
        datasets = dict()
        for hold in hold_list:
            now = str(date.today())
            share_list = Shares.objects.filter(shares_hold_id=hold.id).exclude(date_time__contains=now) \
                .order_by("date_time")
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
        return JsonResponse.OK(data=datasets)


@auth_token()
def day_chart(request):
    if request.method == POST:
        hold_list = SharesHold.objects.filter(is_delete=False)
        datasets = dict()
        now = str(date.today())
        for hold in hold_list:
            share_list = Shares.objects.filter(Q(shares_hold_id=hold.id) &
                                               Q(date_time__contains=now)).order_by("date_time")
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
        hold_list = SharesHold.objects.filter(is_delete=False)
        datasets = dict()
        for hold in hold_list:
            share_list = Shares.objects.filter(shares_hold_id=hold.id).order_by("-date_time")
            share_list = handle_model(list(share_list))
            labels = list()
            data_list = list()
            day_list = list()
            for share in share_list:
                if len((set(day_list))) >= 5:
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
                "days": len((set(day_list)))

            })
        return JsonResponse.OK(data=datasets)


@auth_token()
def ten_chart(request):
    if request.method == POST:
        hold_list = SharesHold.objects.filter(is_delete=False)
        datasets = dict()
        for hold in hold_list:
            share_list = Shares.objects.filter(shares_hold_id=hold.id).order_by("-date_time")
            share_list = handle_model(list(share_list))
            labels = list()
            data_list = list()
            day_list = list()
            for share in share_list:
                if len((set(day_list))) >= 10:
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
                "days": len((set(day_list)))

            })
        return JsonResponse.OK(data=datasets)
