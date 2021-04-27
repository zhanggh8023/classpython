# -*- coding: utf-8 -*-
# @Author  : zgh
# @Email   : 849080458@qq.com
# @File    : logger.py
# @Software: PyCharm

import logging
import time
import os


class Log:

    def __init__ (self, log_name, log_path):
        self.name = log_name
        self.log_path = log_path

    def my_log (self, level, msg):

        loger = logging.getLogger(self.name)
        loger.setLevel(logging.DEBUG)
        # loger.propagate = False  # 关闭系统控制台输出
        formatter = logging.Formatter('%(asctime)s-[%(levelname)s]-%(filename)s-%(name)s-日志信息:%(message)s')

        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        sh.setFormatter(formatter)

        now = time.strftime('%Y-%m-%d_%H_%M_%S')
        new_log_path = self.log_path + "/Api_Autotest_log_{0}.log".format(now[0:10])
        fh = logging.FileHandler(new_log_path, 'a', encoding='utf-8')
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)

        loger.addHandler(sh)
        loger.addHandler(fh)

        if level == 'debug':
            loger.debug(msg)  # 根据level输出日志级别
        elif level == 'info':
            loger.info(msg)
        elif level == 'error':
            loger.error(msg)
        elif level == 'warning':
            loger.warning(msg)

        loger.removeHandler(sh)
        loger.removeHandler(fh)

    def debug (self, msg):
        self.my_log('debug', msg)

    def info (self, msg):
        self.my_log('info', msg)

    def error (self, msg):
        self.my_log('error', msg)

    def warning (self, msg):
        self.my_log('warning', msg)


if __name__ == "__main__":
    logger = Log("summer's log", os.path.dirname(os.getcwd()) + '/Result/log/')
    logger.error("test_p")
