#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: wx_common.py
# 创建时间: 2022/11/27 0027 15:27
# @Version：V 0.1
# @desc :
import requests
import random
import hashlib
from jsonpath import jsonpath
from django.core.cache import cache

from nb.models import Poetry, Author
from public.recommend import recommend_handle, idiom_solitaire, idiom_info
from public.common import surplus_second
from public.conf import *
from public.sensitive import sensitive_words
from public.log import logger


def wx_login():
    wx_token = cache.get("wx_token")
    if wx_token:
        return wx_token
    else:
        url = f" https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={AppID}&secret={AppSecret}"
        try:
            res = requests.get(url=url).json()
            logger.info(f"===================>>>{res}")
            access_token = res["access_token"] if "access_token" in res.keys() else None
            if access_token:
                cache.set("wx_token", access_token, res["expires_in"])
            return access_token
        except Exception as error:
            logger.error(f"微信登录失败. ===>>> {error}")
            return


def wx_media(token: str):
    """
    返回素材media_id
    :param token:
    :return:
    """
    url = f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={token}"
    body = {
        "type": "image",
        "offset": 0,
        "count": 100
    }
    try:
        res = requests.post(url=url, json=body).json()
        media_list = jsonpath(res, "$.item[*].media_id")
        media_id = media_list[random.randint(0, len(media_list) - 1)]
        logger.info(f"media_id: {media_id}")
    except Exception as error:
        logger.error(f"获取media_id出现异常：{error}")
        return
    return media_id


def sign_sha1(signature, timestamp, nonce):
    """
    服务器配置 验证
    :param signature:
    :param timestamp:
    :param nonce:
    :return:
    """
    temp = [TOKEN, timestamp, nonce]
    temp.sort()
    hashcode = hashlib.sha1("".join(temp).encode('utf-8')).hexdigest()
    # logger.info(f"加密：{hashcode}，微信返回：{signature}")
    if hashcode == signature:
        return True


def handle_wx_text(data_list: list):
    content = ""
    for data in data_list:
        content += f"<a href='weixin://bizmsgmenu?msgmenucontent={data.id}&msgmenuid=9528'>{data.name}</a>\n"
    return content


def poetry_by_author_id(author_id: str, skip: int, flag: bool = False):
    """
    诗人对应诗词 更多
    """
    content = ""
    if flag:
        author = Author.objects.get(id=author_id)
        content = author.dynasty.strip("\n") + author.name
    data_list = Poetry.objects.filter(author_id=author_id)[skip: skip + 5]
    if data_list:
        content += "\n诗词推荐：\n"
        content += handle_wx_text(data_list)
        content += ">>> 点击古诗名字 "
        more_text = f"<a href='weixin://bizmsgmenu?msgmenucontent=AUTHOR-{author_id}&msgmenuid=9527'>更多</a>"
        content += "或者查看 " + more_text if len(data_list) == 5 else ""
        cache.set(f"AUTHOR={author_id}", str(skip), 30 * 60)
    return content


def poetry_by_type(text: str, skip: int, val):
    """
    古诗类型 更多
    """
    content = f"古诗类型：{text}\n古诗名字：\n"
    data_list = Poetry.objects.filter(type=text)[skip: skip + 10]
    if data_list:
        content += handle_wx_text(data_list)
        content += ">>> 点击古诗名字 "
        more_text = f"<a href='weixin://bizmsgmenu?msgmenucontent=POETRY_TYPE-{val}&msgmenuid=9529'>更多</a> "
        content += "或者查看 " + more_text if len(data_list) == 10 else ""
        cache.set(f"POETRY_TYPE={val}", str(skip), 30 * 60)
        return content


def author_by_dynasty(text: str, skip: int, val):
    """
    诗人朝代 更多
    """
    content = f"朝代：{text}\n诗人：\n"
    data_list = Poetry.objects.filter(author__dynasty=text)[skip: skip + 10]
    if data_list:
        content += handle_wx_text(data_list)
        content += ">>> 点击诗人名字 "
        more_text = f"<a href='weixin://bizmsgmenu?msgmenucontent=DYNASTY-{val}&msgmenuid=9526'>更多</a> "
        content += "或者查看 " + more_text if len(data_list) == 10 else ""
        cache.set(f"DYNASTY={val}", str(skip), 30 * 60)
        return content


def send_author(data):
    """
    输入作者，返回作者简介及古诗词推荐
    """
    if data.dynasty:
        content = data.dynasty.strip("\n") + data.name
    else:
        content = data.name
    if data.introduce:
        introduce = data.introduce.split("►")[0] if "►" in data.introduce else data.introduce
        content += "\n介绍：\n" + introduce.strip("\n")
    content += poetry_by_author_id(data.id, 0)
    return content


def send_poetry(data):
    """
    输入古诗词名称，返回名句、赏析等数据
    """
    content = f"《{data.name}》\n类型：{data.type}"
    if data.phrase:
        content += "\n名句：\n" + data.phrase.strip("\n")
    if data.explain:
        content += "\n赏析：\n" + data.explain.strip("\n")
    if data.original:
        content += "\n原文：\n" + data.original.strip("\n")
    if data.translation:
        content += "\n译文：\n" + data.translation.strip("\n")
    if data.background:
        content += "\n创作背景：\n" + data.background.strip("\n")
    return content


def send_more(text: str, skip: str, content: str = ""):
    if "DYNASTY=" in text or "POETRY_TYPE=" in text or "AUTHOR=" in text or "RECOMMEND=" in text:
        if str(skip).isdigit():
            skip = int(skip)
            val = text.split("=")[-1]
        else:
            val = str(skip)
            skip = 0
        if "RECOMMEND" in text:
            data = Poetry.objects.get(id=val)
            if data.original:
                content += "原文：\n" + data.original.strip("\n")
            if data.translation:
                content += "\n译文：\n" + data.translation.strip("\n")
            if data.background:
                content += "\n创作背景：\n" + data.background.strip("\n")
        elif "DYNASTY" in text:
            for key, value in DYNASTY.items():
                if int(val) == value:
                    text = key
            content = author_by_dynasty(text, skip + 10, val)
        elif "POETRY_TYPE" in text:
            for key, value in POETRY_TYPE.items():
                if int(val) == value:
                    text = key
            content = poetry_by_type(text, skip + 10, val)
        elif "AUTHOR" in text:
            content = poetry_by_author_id(val, skip=skip + 5, flag=True)
    return content


def poetry_content(text: str, skip: str):
    content = ""
    if skip:
        content = send_more(text, skip)
        return content
    elif len(text) == 32:
        author = Poetry.objects.filter(author_id=text).first()
        if author:
            content = send_author(author)
            return content
        else:
            poetry = Poetry.objects.get(id=text)
            if poetry:
                content = send_poetry(poetry)
                return content
    else:
        if text == "推荐":
            poetry_type = recommend_handle()  # 根据季节、天气返回古诗词类型
            logger.info(f"推荐诗词类型 ===>>> {poetry_type}")
            poetry = Poetry.objects.filter(type=poetry_type).exclude(phrase="").order_by('?').first()
            if poetry:
                phrase = poetry.phrase.strip('\n')
                if poetry.author_id:
                    content = f"今天推荐：\n出自{poetry.author.dynasty}{poetry.author.name}的《{poetry.name}》" \
                              f"\n类型：{poetry_type}\n\n{phrase}\n"
                else:
                    content = f"今天推荐：\n摘自《{poetry.name}》\n类型：{poetry_type}\n\n{phrase}\n"
                if poetry.explain:
                    explain = poetry.explain.strip('\n')
                    content += f"\n赏析：\n{explain}"
                content += "\n>>> 点击查看 " \
                           f"<a href='weixin://bizmsgmenu?msgmenucontent=RECOMMEND-{poetry.id}&msgmenuid=9525'>更多</a>"
                seconds = surplus_second()  # 返回今天剩余秒数
                cache.set(f"RECOMMEND={poetry.id}", str(poetry.id), seconds)
                cache.set(f"recommended-today", content, seconds)
                return content
        for key, value in DYNASTY.items():  # 诗人朝代
            if text == key:
                content = author_by_dynasty(text, 0, value)
                return content
        for key, value in POETRY_TYPE.items():  # 古诗词类型
            if text == key:
                content = poetry_by_type(text, 0, value)
                return content
        data = Poetry.objects.filter(author__name=text).first()
        if data:
            content = send_author(data)
        else:
            data = Poetry.objects.filter(name=text).first()
            if data:
                content = send_poetry(data)
            else:
                data = Poetry.objects.filter(phrase=text).first()  # 古诗名句
                if data:
                    content = f"古诗名字：\n" + f"<a href='weixin://bizmsgmenu?msgmenucontent={data.id}&msgmenuid=9524'>" \
                                           f"{data.name}</a>"
    return content


def send_wx_msg(rec_msg, token: str, skip: str, idiom: str = ""):
    """
    :param db:
    :param request:
    :param rec_msg: 微信返回文案
    :param token: 微信登录token
    :param skip: 更多跳转页数
    :param idiom: 成语接龙
    :return 回复文案和图片id
    """
    content, media_id = "", ""
    if rec_msg.MsgType == 'text':
        text = rec_msg.Content
        logger.info(f"文本信息：{text}")
        if idiom:
            if "IDIOM-INFO" in text:
                idiom_name = text.split("-")[-1]
                content = idiom_info(idiom_name)
            else:
                content = idiom_solitaire(text)
        else:
            content = poetry_content(text, skip)  # 古诗词返回判断
            content = sensitive_words(content) if content else ""
        if not content:
            if text in ["图片", "小七"] and token:
                media_id = wx_media(token)
            elif text in ["all", "文章"]:
                content = ArticleUrl
            elif text in ["follow", "功能"]:
                content = FOLLOW
            else:
                content = text
    elif rec_msg.MsgType == 'event':
        if rec_msg.Event == "subscribe":
            content = FOLLOW
        elif rec_msg.Event == "unsubscribe":
            logger.info(f"用户 {rec_msg.FromUserName} 取消关注了！！！")
    elif rec_msg.MsgType == "image":
        if token:
            media_id = wx_media(token)
        else:
            media_id = rec_msg.MediaId
    return content, media_id
