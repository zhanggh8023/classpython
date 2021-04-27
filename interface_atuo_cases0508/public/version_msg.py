"""
# -------------------------------
# @Time    : 2021/4/19 11:28
# @Author  : zgh
# @Email   : 849080458@qq.com
# @File    : version_msg.py
# -------------------------------
"""

import requests
from public.logger import Log
from conf import Allpath
import time

logger = Log('version_msg', Allpath.log_path)
now = time.strftime('%Y-%m-%d_%H_%M_%S')


def dd_msg():
    url = 'https://oapi.dingtalk.com/robot/send?access_token=dfd67b41b306c26552aab304f54f98bbcfbaf31c39de2422b3b503aaea0f0a5d'

    # 个人测试地址
    # url = 'https://oapi.dingtalk.com/robot/send?access_token=9abe37c6a640422cb85c9a877bb026b0b9029378890c5f14fcc106be9ab5725e'
    headers = {"Content-Type": "application/json"}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "今日测试环境占用情况",
            "text": "### 今日测试环境占用情况：\n"
                    "\n**【H2B2】冒烟测试**==》 \n"
                    "\n1、版本：[refactor1.0-company2.0]，时间：[04.19]；\n"
                    "\n2、版本：[tf-yhtx-0422]，时间：[04.20]；\n"
                    "\n"
                    "\n**【H2B】功能测试**==》 \n"
                    "\n1、版本：[refactor1.0-company2.0]，时间：[04.19]；\n"
                    "\n"
                    "\n**【B2H】功能测试**==》 \n"
                    "\n1、版本：[tf-yhtx-0422]，时间：[04.20]；\n"
                    "\n"
                    "\n**【H2B3】回归测试**==》 \n"
                    "\n1、版本：[]，时间：[]；\n"
                    "\n> ![screenshot]()\n> ###### " + now[0:10] + " 发布 [详情]() \n"
        },
        "at": {
            "atMobiles": [
                "17681829051"
            ],
            "atUserIds ": [
                "章广华"
            ],
            "isAtAll": "true"
        }
    }

    request = requests.post(url, json=data, headers=headers).json()
    logger.info('钉钉机器人消息请求内容{},钉钉机器人消息请求成功{}'.format(data, request))


if __name__ == '__main__':
    dd_msg()
