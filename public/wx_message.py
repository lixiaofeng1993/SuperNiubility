from xml.etree import ElementTree as ET
import time


class ImageMsg:
    def __init__(self, toUser, fromUser, mediaId):
        self._toUser = toUser
        self._fromUser = fromUser
        self._rediaId = mediaId
        self._nowTime = int(time.time())
        self._mediaId = mediaId

    def structReply(self):
        text = """
                <xml>
                <ToUserName><![CDATA[{0}]]></ToUserName>
                <FromUserName><![CDATA[{1}]]></FromUserName>
                <CreateTime>{2}</CreateTime>
                <MsgType><![CDATA[image]]></MsgType>
                <Image>
                <MediaId><![CDATA[{3}]]></MediaId>
                </Image>
                </xml>
                """.format(self._fromUser, self._toUser, self._nowTime, self._mediaId)  # 前面两个参数的顺序需要特别注意
        return text


class Analysis:
    def __init__(self, xmlData):
        print("接收到的数据：" + xmlData)

    def prase(self, xmlText):
        xmlData = ET.fromstring(xmlText)
        msgType = xmlData.find("MsgType").text
        toUserName = xmlData.find("ToUserName").text
        fromUserName = xmlData.find("FromUserName").text
        if msgType == "text":
            content = xmlData.find("Content").text
            TextMsgObj = TextMsg(toUserName, fromUserName, content)
            return TextMsgObj.structReply()
        elif msgType == "image":
            mediaId = xmlData.find("MediaId").text
            ImageMsgObj = ImageMsg(toUserName, fromUserName, mediaId)
            return ImageMsgObj.structReply()


class TextMsg:
    def __init__(self, toUser, fromUser, recvMsg):
        self._toUser = toUser
        self._fromUser = fromUser
        self._recvMsg = recvMsg
        self._nowTime = int(time.time())

    def structReply(self):
        content = self._recvMsg
        text = """
                <xml>
                <ToUserName><![CDATA[{0}]]></ToUserName>
                <FromUserName><![CDATA[{1}]]></FromUserName>
                <CreateTime>{2}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[{3}]]></Content>
                </xml>
                """.format(self._fromUser, self._toUser, self._nowTime, content)  # 前面两个参数的顺序需要特别注意
        return text
