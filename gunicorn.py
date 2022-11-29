#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: gunicorn.py
# 说   明: 
# 创建时间: 2022/1/15 17:27
# @Version：V 0.1
# @desc :
from multiprocessing import cpu_count

bind = '127.0.0.1:8000'
daemon = True  # 守护进程

workers = cpu_count() * 2
worker_class = 'gevent'
forwarded_allow_ips = '*'

# 维持TCP链接
keepalive = 6
timeout = 65
graceful_timeout = 10
worker_connections = 65535

# log
capture_output = True
loglevel = 'info'
accesslog = "/www/wwwlogs/gunicorn_access.log"  # 访问日志文件的路径
errorlog = "/www/wwwlogs/gunicorn_error.log"
