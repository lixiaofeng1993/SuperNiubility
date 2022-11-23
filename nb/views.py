from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.db.models import Q  # 与或非 查询
from datetime import date

from .tasks import make_overdue_todo
from nb.models import ToDo
from public.conf import GET, POST, NumberOfPages
from public.auth_token import auth_token
from public.common import handle_json, pagination_data, handle_model, request_get_search
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
        todo_list = self.model.objects.filter(is_delete=False).order_by("-create_date")
        todo_list = handle_model(list(todo_list))
        return todo_list

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
        print(td.is_done)
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
