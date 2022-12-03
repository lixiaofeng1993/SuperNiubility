#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: send_email.py
# 创建时间: 2022/12/2 0002 23:27
# @Version：V 0.1
# @desc :
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# from email.header import Header

from public.conf import EmailPassword
from public.log import logger


def send_email(from_email, to_email: str, code: str):
    """
    发送邮件
    :param from_email: 发件人
    :param to_email: 收件人
    :param code: 验证码
    :return:
    """
    smtp_service = "smtp.163.com"
    msg = MIMEMultipart()
    msg['Subject'] = "Super Niubility账号--邮箱安全验证"
    msg['from'] = from_email
    msg['to'] = to_email
    msg["Accept-Language"] = "zh-CN"
    msg["Accept-Charset"] = "ISO-8859-1,utf-8"
    # 邮件正文
    html = f"""
        <html>
        <head></head>
        <body>
            <p style="color: #333;font-weight: bold;line-height: 30px;">亲爱的用户：</p>
            <p style="line-height: 30px;color: #333;">您好！感谢您使用Super Niubility，本次邮箱验证请求的验证码为：</p>
            <p style="color: red;font-size: 18px;">{code}<span style="color: #979797;font-size: 12px;">（为保证您账号的安全性，请在1小时内完成验证.）</span></p>
        </body>
        </html>
    """
    body = MIMEText(html, "html")
    msg.attach(body)
    try:
        s = smtplib.SMTP_SSL(smtp_service)
        s.login(from_email, EmailPassword)
        s.sendmail(from_email, to_email, msg.as_string())
        s.quit()
        logger.info(f"{to_email} 邮件发送成功")
        return True
    except smtplib.SMTPException as error:
        logger.error(f"{to_email} 发送邮件出现异常 ===>>> {error}")
    except Exception as error:
        logger.error(f"{to_email} 发送邮件出现未知异常 ===>>> {error}")
