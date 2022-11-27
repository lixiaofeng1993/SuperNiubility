#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: wx_message.py
# 创建时间: 2022/11/27 0027 15:38
# @Version：V 0.1
# @desc :
import time
import xml.etree.ElementTree as Et

from public.log import logger


def parse_xml(web_data):
    xml_data = Et.fromstring(web_data)
    try:
        msg_type = xml_data.find('MsgType').text
    except Exception as error:
        logger.error(f"解析微信XML消息，获取 MsgType 文案报错 ===>>> {error}")
        return
    if msg_type == 'text':
        return TextMsg(xml_data)
    elif msg_type == 'event':
        return EventMsg(xml_data)
    elif msg_type == "image":
        return ImageMsg(xml_data)


class Msg(object):
    def __init__(self, xml_data):
        self.ToUserName = xml_data.find('ToUserName').text
        self.FromUserName = xml_data.find('FromUserName').text
        self.CreateTime = xml_data.find('CreateTime').text
        self.MsgType = xml_data.find('MsgType').text


class TextMsg(Msg):
    def __init__(self, xml_data):
        Msg.__init__(self, xml_data)
        self.Content = xml_data.find('Content').text


class EventMsg(Msg):
    def __init__(self, xml_data):
        Msg.__init__(self, xml_data)
        self.Content = xml_data.find('EventKey').text
        self.Event = xml_data.find('Event').text


class ImageMsg(Msg):
    def __init__(self, xml_data):
        Msg.__init__(self, xml_data)
        self.MediaId = xml_data.find('MediaId').text


class Message:
    def __init__(self, to_user, from_user, content="", media_id="", msg_type="text"):
        self.to_user = to_user
        self.from_user = from_user
        self.content = content
        self.media_id = media_id
        self.msg_type = msg_type
        self.message = ""

    def send(self):
        if self.msg_type == "text":
            self.message = f"""
                        <xml>
                        <ToUserName><![CDATA[{self.to_user}]]></ToUserName>
                        <FromUserName><![CDATA[{self.from_user}]]></FromUserName>
                        <CreateTime>{int(time.time())}</CreateTime>
                        <MsgType><![CDATA[text]]></MsgType>
                        <Content><![CDATA[{self.content}]]></Content>
                        </xml>
                   """
            logger.info(f"微信回复消息文案长度 {len(self.content)}")
        elif self.msg_type == "image":
            self.message = f"""
                    <xml>
                      <ToUserName><![CDATA[{self.to_user}]]></ToUserName>
                      <FromUserName><![CDATA[{self.from_user}]]></FromUserName>
                      <CreateTime>{int(time.time())}</CreateTime>
                      <MsgType><![CDATA[image]]></MsgType>
                      <Image>
                        <MediaId><![CDATA[{self.media_id}]]></MediaId>
                      </Image>
                    </xml>
                    """
            logger.info(f"微信回复图片 {self.media_id}")
        return self.message
