#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: gunicorn.py
# 说   明: 
# 创建时间: 2022/1/15 17:27
# @Version：V 0.1
# @desc :

from multiprocessing import cpu_count

# debug = True
# 修改代码时自动重启
# reload = True

reload_engine = 'inotify'
# //绑定与Nginx通信的端口
# bind = '127.0.0.1:3002'
bind = '0.0.0.0:8000'
# pidfile = 'www/gunicorn.pid'

daemon = True  # 守护进程

# workers = 4  # 进程数
workers = cpu_count() * 2 + 1  # 进程数
# workers = 1  # 进程数

worker_class = 'gevent'  # 默认为阻塞模式，最好选择gevent模式,默认的是sync模式

# 维持TCP链接
keepalive = 6
timeout = 65
graceful_timeout = 10
worker_connections = 65535

# 日志级别
# debug:调试级别，记录的信息最多；
# info:普通级别；
# warning:警告消息；
# error:错误消息；
# critical:严重错误消息；
loglevel = 'info'
# 访问日志路径
accesslog = '/www/wwwlogs/gunicorn_access.log'
# 错误日志路径
errorlog = '/www/wwwlogs/gunicorn_error.log'
# 设置gunicorn访问日志格式，错误日志无法设置
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'

# 执行命令
# gunicorn -c gconfig.py main:app
# gunicorn -c gconfig.py main:app -k uvicorn.workers.UvicornWorker

'''
自动执行
使用 supervisor
https://docs.gunicorn.org/en/stable/deploy.html#supervisor
参考资料：
https://www.jianshu.com/p/bbd0b4cfcac9
https://www.cnblogs.com/tk091/archive/2014/07/22/3859514.html
'''
