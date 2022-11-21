import json
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.contrib import auth  # django认证系统
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from public.jwt_sign import create_access_token
from public.conf import ACCESS_TOKEN_EXPIRE_MINUTES, GET, POST
from public.response import JsonResponse
from public.common import handle_json
from public.log import logger


@login_required
def index(request):
    return render(request, "home/index.html")


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
        return JsonResponse.OK(data=result)


@login_required
def logout(request):
    username = request.session.get("user")
    cache.delete(username)
    auth.logout(request)  # 退出登录
    response = HttpResponseRedirect('/login/action/')
    return response


def page_not_found(request, exception, template_name='home/404.html'):
    logger.error(f"页面出现异常 ===>>> {exception}")
    return render(request, template_name)


def server_error(exception, template_name='home/500.html'):
    logger.error(f"系统出现异常 ===>>> {exception}")
    return render(exception, template_name)
