# -*- coding: utf-8 -*-
# @Author  : zgh
# @Email   : 849080458@qq.com
# @File    : manage.py
# @Software: PyCharm

import datetime
import time
import unittest
import warnings
import Levenshtein
from ddt import ddt, data, unpack
from conf import Allpath
from public.all_method import assert_value_result, data_value_result, data_value_replace, many_data_result, \
    mk_new_process, url_value_result, sql_value_result, idlist_value_result, data_number_replace, projectenv, \
    ding_report_url, data_type_replace
from public.config import config
from public.get_mysql_info import getMysqlInfo
from public.httpRequest import httpRequest
from public.logger import Log
from public.readExcel import readExcel
from public.writeExcel import writeExcel

logger = Log('Unit_test', Allpath.log_path)
s = config().read_config(Allpath.case_conf_path, 'SHEET', 'sheet')
logger.info('当前使用的用例集表单：{}'.format(ding_report_url()[0:-7]))

h = readExcel(Allpath.test_data_path, s)
data2 = h.read_Excel()
t = writeExcel(Allpath.test_data_path, s)
mode = config().read_config(Allpath.case_conf_path, 'FLAG', 'mode')
ID = config().read_config(Allpath.case_conf_path, 'FLAG', 'case_list')


@ddt  # 用ddt装饰我的测试类
class TestHttpRequset(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter('ignore', ResourceWarning)
        logger.info("============我要开始测试了===============")

    @data(*data2)  # 用data 来装饰我的测试用例
    # 加一个* 号可以进行区分单个执行
    @unpack
    def test_jkgl(self, id, method, url, data, code, case_name, sql, env, assert_value):

        logger.info(
            "正在执行第{}条用例:{}——当前请求内容_URL：{}；method：{}；data：{}；sql：{}".format(id, case_name, url, method, data, sql))
        result_dict = {}
        result_dict['data'] = []

        # 预处理请求内容中需要替换的关联参数值
        if len(assert_value) > 0:
            if type(assert_value[0]) is dict and 'id' in assert_value[0].keys():
                data = data_value_result(data, assert_value[0])
            elif type(assert_value[0]) is dict and 'idlist' in assert_value[0].keys():
                data = idlist_value_result(data, assert_value[0])
            elif type(assert_value[0]) is dict and 'path' in assert_value[0].keys():
                url = url_value_result(url, assert_value[0])
            elif type(assert_value[0]) is dict and 'my_sql' in assert_value[0].keys():
                data = sql_value_result(data, assert_value[0])
            elif type(assert_value[0]) is dict:
                data = many_data_result(data, assert_value[0])

        if 'random' in env.keys():
            # 获取随机名称
            data = data_value_replace(env['random'], data)
        elif 'randomtype' in env.keys():
            # 获取随机身份证号/手机号
            randomdata = data_type_replace(env['randomtype'], data)
            data = randomdata[0]
            result_dict['data'] = randomdata[1]
        elif 'randompath' in env.keys():
            try:
                randompath = data_number_replace(env['randompath'], url)
                url = randompath[0]
            except:
                randompath = data_number_replace(env['randompath'], data)
                data = randompath[0]
            result_dict['data'] = randompath[1]

        # 打印出来接口返回时间
        since = datetime.datetime.now()
        result = httpRequest().httpGet(url, method, eval(data), sql, env)
        time_elapsed = datetime.datetime.now() - since
        logger.info('Testing complete in {}s'.format(time_elapsed.total_seconds()))
        result_dict['time'] = time_elapsed.total_seconds()

        # 判断请求返回内容是否包含key值：result
        if 'result' in result.keys():
            result_dict['data'] = result['result']
            if 'message' in result.keys():
                result_dict['data'] = result['message']
            elif 'randomtype' in env.keys():
                if result_dict['data'] == None:
                    result_dict['data'] = []
                result_dict['data'].append(randomdata[1])
        elif 'data' in result.keys():
            if 'randompath' in env.keys():
                result_dict['data'].append(result['data'])
            else:
                result_dict['data'] = result['data']
        # 请求返回后不同渠道平台code获取判断处理
        if 'responseCode' in result.keys():
            value = str(result['responseCode'])
            if 'message' in result.keys():
                result_dict['data'].append(result['message'])
            if 'cooperationOrderInfo' in result.keys():
                result_dict['data'].append(result['cooperationOrderInfo'])
            if 'uniqReserveCode' in result.keys():
                result_dict['data'].append(result['uniqReserveCode'])
        elif 'response_code' in result.keys():
            value = str(result['response_code'])
            if 'msg' in result.keys():
                result_dict['data'].append(result['msg'])
            if 'revision_info' in result.keys():
                result_dict['data'].append(result['revision_info'])
            if 'uniqReserveCode' in result.keys():
                result_dict['data'].append(result['uniqReserveCode'])
        elif 'status' in result.keys():
            value = str(result['status'])
        elif 'code' in result.keys():
            value = str(result['code'])
        else:
            value = str(result['responseResult'])

        if value != '0' and value != '200':
            if 'errorMsg' in result.keys():
                result_dict['data'] = result['errorMsg']
            elif 'msg' in result.keys():
                result_dict['data'] = result['msg']
            else:
                result_dict['data'] = result['message']

        logger.info('接口返回message:{}'.format(result_dict['data']))

        # 返回值中提取需要对比断言的内容
        if len(assert_value) > 0 and type(assert_value[0]) is list:
            value = assert_value_result(result, assert_value[0])
        elif len(assert_value) > 1:
            value = assert_value_result(result, assert_value[1])
        result_dict['code'] = value

        try:
            # 断言对比(期望值，实际返回值)
            self.assertEqual(code, value)
            result_dict['result'] = 'pass'
            logger.info('用例code比对成功！实际返回:{}'.format(value))
        except Exception as e:
            result_dict['result'] = 'fail'
            result_dict["sql_result"] = 'fail'
            logger.warning('用例code比对失败！实际返回：%s' % value)
            t.write_Excel(id + 1, result_dict)
            raise e
        if 'my_sql' in sql.keys():
            sql_result = getMysqlInfo(projectenv[1]).get_mysql_info(sql['my_sql'], sql['condition'],
                                                                    sql['code'])
            try:
                if 'sql' in sql.keys() and sql['sql'] == 0:
                    # 短信内容进行相似度匹配值
                    similarity = Levenshtein.ratio(str(sql_result[0]), str(sql['result']))
                    if similarity > 0.9:
                        logger.info('实际值对比期望值的相似度：{}'.format(similarity))
                    else:
                        self.assertEqual(sql_result[0], sql['result'])
                else:
                    self.assertEqual(str(sql_result[0]), str(sql['result']))
                result_dict["sql_result"] = 'pass'
                logger.info('用例sql比对执行成功！实际返回：%s' % sql_result[0])
            except Exception as e:
                result_dict["sql_result"] = 'fail'
                logger.warning('执行用例sql比对报错：{}，数据库返回：{}'.format(e, sql_result[0]))
                raise e
        else:
            result_dict["sql_result"] = 'pass'
        logger.info("返回数据写入excel：{}".format(result_dict))
        t.write_Excel(id + 1, result_dict)

        if 'new' in env.keys() and env['new'] == 1:
            mk_new_process(result['result'])
        if 'weiyi' in env.keys():
            getMysqlInfo(projectenv[1]).update_weiyi_refund(env)

        # 指定用例等待时间控制
        if 'time' in env.keys():
            time.sleep(env['time'])
            logger.info("用例{}执行完成进行等待{}s".format(id, env['time']))

    def tearDown(self):

        logger.info("===============我要结束测试了！==================")


if __name__ == '__main__':
    unittest.main()
