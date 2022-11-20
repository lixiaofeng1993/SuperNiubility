from django.shortcuts import render, redirect
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.contrib import auth  # django认证系统
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required

from public.jwt_sign import create_access_token
from public.auth_token import auth_token
from public.conf import ACCESS_TOKEN_EXPIRE_MINUTES, GET, POST
from public.response import JsonResponse
from public.log import logger


@login_required
def index(request):
    return render(request, "home/index.html")


def login(request):
    if request.method == GET:
        return render(request, "login/login.html")
    elif request.method == POST:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is None:
            result = {"error": f"用户名或密码错误."}
            return render(request, "login/login.html", result)
        auth.login(request, user)
        token = cache.get(username)
        request.session["user"] = username
        response = HttpResponseRedirect('/')
        if token:
            return response
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token({"sub": username}, expires_delta=access_token_expires)
        cache.set(username, token, ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        return response


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
