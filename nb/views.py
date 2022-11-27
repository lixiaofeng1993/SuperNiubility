import efinance as ef
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Q  # 与或非 查询
from django.contrib.auth.decorators import login_required

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
    paginate_by = NumberOfPages / 5

    def dispatch(self, *args, **kwargs):
        return super(StockIndex, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        model = model_superuser(self.request, self.model)
        obj_list = model.filter(is_delete=False).order_by("-create_date")
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
                model.filter(Q(id=stock_id) & Q(is_delete=False)).update(
                    name=name, code=code, number=number, cost_price=cost_price, color=color, user_id=user_id
                )
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
        delete_cache(user_id)
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
        delete_cache(user_id)
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
    return render(request, "home/record/look_record.html", info)
