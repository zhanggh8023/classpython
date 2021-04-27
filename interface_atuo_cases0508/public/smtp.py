# -*- coding: utf-8 -*-
# @Author  : zgh
# @Email   : 849080458@qq.com
# @File    : smtp.py
# @Software: PyCharm


import smtplib
import configparser
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from conf import Allpath
from public.logger import Log
from public.get_mysql_info import getMysqlInfo
from public.all_method import ding_report_url, projectenv
from public.config import config

gmi = getMysqlInfo(projectenv[2])
logger = Log('smtp', Allpath.log_path)


class massageMail:
    def read_config(self, conf_path, section, option):
        tt = configparser.ConfigParser()
        tt.read(conf_path, encoding='utf-8')
        result = eval(tt.get(section, option, ))
        return result

    def Message (self, filename, receivers, ):
        data = massageMail().read_config(Allpath.smtp_conf_path, 'STMPMASSAGEMIAL', 'config')
        s = config().read_config(Allpath.case_conf_path, 'SHEET', 'sheet')
        data['subject'] = ding_report_url()
        text = eval(gmi.get_mysql_info_test("select * from jkgl ORDER BY date DESC LIMIT 10;", 1)['restult'])

        # Python 发送带附件的邮件
        mail_host = data['mail_host']  # 设置服务器
        mail_user = data['mail_user']  # 用户名
        mail_pass = data['mail_pass']  # 口令
        # receivers = data['receivers']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        # acc = data['acc']
        address = Allpath.html_path

        # 创建一个带附件的实例
        message = MIMEMultipart()
        message['From'] = Header(data['From'], 'utf-8')  # 邮件名字
        message['To'] = Header(receivers, 'utf-8')
        subject = data['subject']
        message['Subject'] = Header(subject, 'utf-8')

        # 邮件正文内容
        message.attach(MIMEText('\n测试人员:' + str(text['testname']) + '\n开始时间:' + str(text['time']) + '\n合计耗时:' + str(
            text['sumtime']) + '\n本次结果:' + str(text['testresult']) + '\n通过率:' + str(text['tonggl']) + '\n\n' + data[
                                    'MIMEText'] + '\n\n' + "接口自动化测试报告【Python】：http://122.224.247.100:8508/" + s + ".html",
                                'plain',
                                'utf-8'))

        # 构造附件1，传送当前目录下的 smtp.txt 文件
        att1 = MIMEText(open(address + '/' + filename + '.html', 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        att1["Content-Disposition"] = 'attachment; filename="interface_smtp.html"'
        message.attach(att1)

        try:
            s = smtplib.SMTP_SSL(mail_host, 465)  # 连接上邮箱服务器
            s.login(mail_user, mail_pass)
            s.sendmail(mail_user, receivers.split(','), message.as_string())
            logger.info("邮件发送成功")
        except smtplib.SMTPException as e:
            logger.error("Error: 无法发送邮件")
            raise e


if __name__ == '__main__':
    now = time.strftime('%Y-%m-%d_%H_%M_%S')
    massageMail().Message(now, '849080458@qq.com')
