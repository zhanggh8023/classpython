import unittest
import time, shutil
import HTMLTestRunner_zgh
from public import Unit_test
from conf import Allpath
from public.config import config
from public.writeExcel import writeExcel
from public.logger import Log
from public.smtp import massageMail
from public.all_method import ding_msg, order_time_init, ding_report_url


logger = Log('main', Allpath.log_path)

data_t = time.strftime('%Y-%m-%d')
s = config().read_config(Allpath.case_conf_path, 'SHEET', 'sheet')
# 2019年7月22日 10:40:51新增执行前清理Sheet1原始用例结果记录
writeExcel(Allpath.test_data_path, s).Excel_dellog()
# 初始化医院后台时间段可约
order_time_init()


suite = unittest.TestSuite()  # 实例
loader = unittest.TestLoader()
# 测试模块
suite.addTest(loader.loadTestsFromModule(Unit_test))

now = time.strftime('%Y-%m-%d_%H_%M_%S')
file_path = Allpath.html_path + '/' + now + '.html'

with open(file_path, 'wb+') as file:
    # 实例化测试报告运行
    runner = HTMLTestRunner_zgh.HTMLTestRunner(stream=file, verbosity=2, tester='测试组自动化报告', title=ding_report_url(),
                                               description='该测试报告仅体现某接口请求以及参数值验证情况。')
    # 传入测试运行对象
    runner.run(suite)

# 当前时间，邮件对象
# name=['zhanggh@helianhealth.com',]
# name = ['zhanggh@helianhealth.com', ]
# for i in range(len(name)):
#     try:
#         massageMail().Message(now, name[i])
#         logger.info('发送邮箱为：%s' % name[i])
#     except:
#         continue
# logger.info('本次Python接口自动化框架执行完毕！%s' % time.strftime('%Y-%m-%d %H:%M:%S'))


# # 备份报告及用例执行结果
# shutil.copyfile(Allpath.html_path + '/' + now + '.html', '../report/index/' + s + '.html')
# shutil.copyfile(Allpath.html_path + '/' + now + '.html', '../report/' + now + '.html')  # 备份报告
# shutil.copyfile(Allpath.test_data_path, '../case/' + now + '.xlsx')  # 备份用例结果
#
#
# # 发送钉钉消息
# ding_msg(now)
