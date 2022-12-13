import re
from django.shortcuts import render
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.contrib import auth  # django认证系统
from django.db.models import Q  # 与或非 查询
from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from public.jwt_sign import create_access_token
from public.conf import *
from public.send_email import send_email
from public.response import JsonResponse
from public.common import handle_json, home_poetry, operation_record, surplus_second, randint, random_str
from public.log import logger


@login_required
def index(request):
    obj_list = cache.get(RECOMMEND)
    if not obj_list:
        obj_list = home_poetry()
    return render(request, "home/index.html", {"obj": obj_list})


def login(request):
    if request.method == GET:
        num = randint(0, BackgroundNumber)
        url = BackgroundName.format(num=num)
        return render(request, "login/login.html", {"url": url})
    elif request.method == POST:
        body = handle_json(request)
        if not body:
            return JsonResponse.JsonException()
        username = body.get('username', '')
        password = body.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is None:
            return JsonResponse.CheckException()
        auth.login(request, user)
        user = User.objects.get(username=username)
        token = cache.get(username)
        request.session["user"] = username
        request.session["user_id"] = user.id
        request.session["super"] = user.is_superuser  # 是否是超级管理员
        login_from = request.session.get("login_from")
        logger.info(f"地址来源 ===>>> {login_from}")
        result = {
            "id": user.id,
            "username": username,
            "token": token,
            "login_from": login_from
        }
        if not token:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            token = create_access_token({"sub": username}, expires_delta=access_token_expires)
            cache.set(username, token, ACCESS_TOKEN_EXPIRE_MINUTES * 60)
            result["token"] = token
        repr = "登录"
        msg = f"用户 {username} {repr}系统"
        operation_record(request, user, user.id, repr, "", msg)
        return JsonResponse.OK(data=result)


def change(request):
    if request.method == GET:
        num = randint(0, BackgroundNumber)
        url = BackgroundName.format(num=num)
        return render(request, "login/change.html", {"url": url})
    elif request.method == POST:
        body = handle_json(request)
        if not body:
            return JsonResponse.JsonException()
        username = body.get('username', '')
        password = body.get('password', '')
        confirm = body.get('confirm', '')
        to_email = body.get('email', '')
        _code = body.get('code', '')
        if password != confirm:
            return JsonResponse.EqualException()
        repeat = cache.get(ToEmail.format(email=to_email))
        if not repeat:
            return JsonResponse.AgreementException()
        user = User.objects.filter(username=username).first()
        if not user:
            return JsonResponse.UserException()
        if user.email != to_email:
            return JsonResponse.JsonException()
        cache_code = cache.get(VerificationCode)
        if _code != cache_code:
            return JsonResponse.CodeException()
        check = auth.authenticate(username=username, password=password)
        if check:
            return JsonResponse.RepeatException()
        try:
            user.set_password(password)
            user.email = to_email
            user.save()
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        repr = "登录"
        msg = f"用户 {username} 修改密码"
        operation_record(request, user, user.id, repr, "", msg)
        return JsonResponse.OK()


def register(request):
    if request.method == GET:
        num = randint(0, BackgroundNumber)
        url = BackgroundName.format(num=num)
        return render(request, "login/register.html", {"url": url})
    elif request.method == POST:
        body = handle_json(request)
        if not body:
            return JsonResponse.JsonException()
        username = body.get('username', '')
        password = body.get('password', '')
        confirm = body.get('confirm', '')
        to_email = body.get('email', '')
        _code = body.get('code', '')
        if password != confirm:
            return JsonResponse.EqualException()
        repeat = cache.get(ToEmail.format(email=to_email))
        if not repeat:
            return JsonResponse.AgreementException()
        cache_code = cache.get(VerificationCode)
        if _code != cache_code:
            return JsonResponse.CodeException()
        user = User.objects.filter(username=username).exists()
        if user:
            return JsonResponse.RepeatException()
        try:
            user = User.objects.create_user(username=username, password=password, email=to_email)
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        repr = "登录"
        msg = f"用户 {username} 注册系统"
        operation_record(request, user, user.id, repr, "", msg)
        return JsonResponse.OK()


def email(request):
    if request.method == POST:
        body = handle_json(request)
        if not body:
            return JsonResponse.JsonException()
        user = User.objects.filter(Q(is_superuser=1) & Q(is_active=1) & Q(is_staff=1)).exclude(email="").first()
        if not user:
            return JsonResponse.ServerError()
        to_email = body.get("email")
        if not re.match("\w+@\w+\.\w+", to_email):
            return JsonResponse.CheckException()
        repeat = cache.get(ToEmail.format(email=to_email))
        if repeat:
            return JsonResponse.RepeatException()
        salt = cache.get(VerificationCode)
        cache.set(ToEmail.format(email=to_email), True, EmailTimeout)
        if not salt:
            salt = random_str()
            cache.set(VerificationCode, salt, EmailTimeout)
        msg = send_email(user.email, to_email, salt)
        if not msg:
            return JsonResponse.BadRequest()
        return JsonResponse.OK()


@login_required
def code(request):
    if request.method == GET:
        salt = cache.get(VerificationCode)
        if not salt:
            salt = random_str()
            cache.set(VerificationCode, salt, EmailTimeout)
        return JsonResponse.OK(data={"code": salt})


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
