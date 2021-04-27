# ————————————————
# @Time    : 2020/12/8 10:09
# @Author  : zgh
# @Email   : 849080458@qq.com
# @File    : Property.py
# ————————————————


from public.config import config
from public.readExcel import readExcel
from public.writeExcel import writeExcel
from public.logger import Log
from conf import Allpath
from public.PropertyTest import property, run_test

logger = Log('Property', Allpath.log_path)

s = config().read_config(Allpath.case_conf_path, 'SHEET', 'sheet')
logger.info('当前使用的用例表单：{}'.format(s))

h = readExcel(Allpath.test_data_path, s)
data2 = h.read_Excel()
t = writeExcel(Allpath.test_data_path, s)
mode = config().read_config(Allpath.case_conf_path, 'FLAG', 'mode')
ID = config().read_config(Allpath.case_conf_path, 'FLAG', 'case_list')

# 数据处理
def run (pool, num):
    for i in range(len(data2)):
        logger.info('正在执行第{}条用例:{}'.format(data2[i]['id'], data2[i]['case_name']))
        time_data = run_test(data2[i], pool, num)
        logger.info('正在写入第{}条用例性能测试时间:{}'.format(data2[i]['id'], time_data))
        t.write_time(data2[i]['id'], time_data)


if __name__ == '__main__':
    run(10, 20)
