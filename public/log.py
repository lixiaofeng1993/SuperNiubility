#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# 创 建 人: 李先生
# 文 件 名: log.py
# 创建时间: 2022/10/14 0014 21:52
# @Version：V 0.1
# @desc :
import logging
import os
import time
from logging.handlers import RotatingFileHandler

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def mkdir(path) -> str:
    """
    检查目录是否存在，不存在则创建
    :param path:
    :return:
    """
    if not os.path.exists(path):
        os.mkdir(path)
    return path


LOG_PATH = mkdir(os.path.join(BASE_PATH, "log"))


class Log:

    def __init__(self):
        self.logName = os.path.join(LOG_PATH, "{}.log".format(time.strftime("%Y-%m-%d")))
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter(
            '[%(asctime)s][%(filename)s %(lineno)d][%(levelname)s]: %(message)s')

        # 创建一个FileHandler，用于写到本地
        fh = RotatingFileHandler(filename=self.logName, mode='a', maxBytes=1024 * 1024 * 5, backupCount=10,
                                 encoding='utf-8')  # 使用RotatingFileHandler类，滚动备份日志
        fh.setLevel(logging.INFO)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)

        # 创建一个StreamHandler,用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)

        # 这两行代码是为了避免日志输出重复问题
        # self.logger.removeHandler(ch)
        # self.logger.removeHandler(fh)
        # fh.close()  # 关闭打开的文件


logger = Log().logger
if __name__ == '__main__':
    logger.info("---测试开始---")
    logger.debug("---测试结束---")
