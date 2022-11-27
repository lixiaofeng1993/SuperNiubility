import json
from django.shortcuts import render
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.contrib import auth  # django认证系统
from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from public.jwt_sign import create_access_token
from public.conf import ACCESS_TOKEN_EXPIRE_MINUTES, GET, POST
from public.response import JsonResponse
from public.common import handle_json, home_poetry, operation_record
from public.log import logger


@login_required
def index(request):
    user_id = request.session.get("user_id")
    obj_list = home_poetry(user_id)
    return render(request, "home/index.html", {"obj": obj_list})


def login(request):
    if request.method == GET:
        return render(request, "login/login.html")
    elif request.method == POST:
        body = handle_json(request)
        if not body:
            return JsonResponse.JsonException()
        username = body.get('username', '')
        password = body.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is None:
            result = {"error": f"用户名密码错误."}
            return JsonResponse.CheckException(data=result)
        auth.login(request, user)
        user = User.objects.get(username=username)
        token = cache.get(username)
        request.session["user"] = username
        request.session["user_id"] = user.id
        request.session["super"] = user.is_superuser  # 是否是超级管理员
        result = {
            "id": user.id,
            "username": username,
            "token": token
        }
        if not token:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            token = create_access_token({"sub": username}, expires_delta=access_token_expires)
            cache.set(username, token, ACCESS_TOKEN_EXPIRE_MINUTES * 60)
            result["token"] = token
        repr = "登录"
        msg = f"{username} {repr}系统"
        operation_record(request, user, user.id, repr, "", msg)
        return JsonResponse.OK(data=result)


@login_required
def logout(request):
    username = request.session.get("user")
    cache.delete(username)
    auth.logout(request)  # 退出登录
    response = HttpResponseRedirect('/login/action/')
    user = User.objects.get(username=username)
    repr = "退出"
    msg = f"{username} {repr}系统"
    operation_record(request, user, user.id, repr, "", msg)
    return response


def page_not_found(request, exception, template_name='home/404.html'):
    logger.error(f"页面出现异常 ===>>> {exception}")
    return render(request, template_name)


def server_error(exception, template_name='home/500.html'):
    logger.error(f"系统出现异常 ===>>> {exception}")
    return render(exception, template_name)
