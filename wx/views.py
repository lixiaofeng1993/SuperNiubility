from starlette.responses import HTMLResponse, Response
from django.views import View

from public.wx_common import *
from public.wx_message import parse_xml, Message


class WechatServe(View):

    def get(self, request, *args, **kwargs):
        signature = request.GET.get("signature")
        timestamp = request.GET.get("timestamp")
        nonce = request.GET.get("nonce")
        echostr = request.GET.get("echostr")
        try:
            if sign_sha1(signature, timestamp, nonce):
                return int(echostr)
            else:
                logger.error("加密字符串 不等于 微信返回字符串，验证失败！！！")
                return "验证失败！"
        except Exception as error:
            return f"微信服务器配置验证出现异常:{error}"

    def post(self, request, *args, **kwargs):
        try:
            res = requests.get("http://121.41.54.234/wx/login").json()
            token = res["result"]["access_token"]
        except Exception as error:
            logger.error(f"获取微信登录token出现异常：{error}")
            token = ""
        try:
            rec_msg = parse_xml(request.body())
            if not rec_msg:
                return HTMLResponse('success')
            to_user = rec_msg.FromUserName
            from_user = rec_msg.ToUserName
            text = rec_msg.Content
            content, media_id, skip = "", "", ""
            idiom = cache.get("IDIOM")
            if text:
                if text == "推荐":
                    content = cache.get("recommended-today")
                elif text and (
                        "DYNASTY" in text or "POETRY_TYPE" in text or "AUTHOR" in text or "RECOMMEND" in text):
                    skip = cache.get(text)
                    if not skip:
                        content = "会话只有30分钟，想了解更多，请重新发起~"
                elif not idiom and text in ["成语接龙", "接龙"]:
                    cache.sete(key=f"IDIOM", value=text, seconds=30 * 60)
                    content = "进入时效30分钟的成语接龙时刻，输入成语开始吧~"
                elif not idiom and "IDIOM-INFO" in text:
                    content = "成语接龙会话时效只有30分钟，想了解更多，请重新发起~"
                elif idiom and text == "exit":
                    cache.delete("IDIOM")
                    content = "See you later..."
            if not content:
                content, media_id = send_wx_msg(rec_msg, token, skip, idiom)
            if rec_msg.MsgType == 'text' and not media_id:
                if "</a>" in content and len(content) >= 2000:
                    content = "..." + content[len(content) - 2000:]
                elif len(content) >= 710 and "</a>" not in content:
                    content = content[:710] + "..."
                return Response(
                    Message(to_user, from_user, content=content).send(),
                    media_type="application/xml")
            elif rec_msg.MsgType == 'event' and content:
                return Response(
                    Message(to_user, from_user, content=content).send(), media_type="application/xml")
            elif rec_msg.MsgType == "image" or media_id:
                return Response(
                    Message(to_user, from_user, media_id=media_id, msg_type="image").send(),
                    media_type="application/xml")
        except Exception as error:
            logger.error(f"微信回复信息报错：{error}")
            return HTMLResponse('success')
