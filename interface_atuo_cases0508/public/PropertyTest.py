# ————————————————
# @Time    : 2020/12/8 14:30
# @Author  : zgh
# @Email   : 849080458@qq.com
# @File    : PropertyTest.py
# ————————————————

from public.logger import Log
from conf import Allpath
from public.get_mysql_info import getMysqlInfo
from public.httpRequest import httpRequest
from public.all_method import assert_value_result, data_value_result, data_value_replace, many_data_result, \
    data_number_replace, idlist_value_result, url_value_result, projectenv
import datetime, requests
import multiprocessing
import asyncio
import numpy as np

logger = Log('PropertyTest', Allpath.log_path)


# 定义异步函数
async def hello (num, msg, ii):
    try:
        since = datetime.datetime.now()
        result = httpRequest().httpGet(num['url'], num['method'], eval(num['data']), num['sql'], num['env'])
        # result = requests.get(num['url'],eval(num['data']),).json()
        time_elapsed = datetime.datetime.now() - since
        logger.info('{},start{},Testing complete in {}s'.format(msg, since, time_elapsed.total_seconds()))
        result_dict = {'id': ii, 'result': result, 'time_elapsed': time_elapsed.total_seconds()}
    except:
        result_dict = {'id': ii, 'result': {'code': 1, 'result': ''}, 'time_elapsed': 0}

    return result_dict


def run_test (case, pool, num):
    loop = asyncio.get_event_loop()
    result = []
    if len(case['assert_value']) > 0:
        if type(case['assert_value'][0]) is dict and 'id' in case['assert_value'][0].keys():
            case['data'] = data_value_result(case['data'], case['assert_value'])
        elif type(case['assert_value'][0]) is dict and 'idlist' in case['assert_value'][0].keys():
            case['data'] = idlist_value_result(case['data'], case['assert_value'][0])
        elif type(case['assert_value'][0]) is dict and 'path' in case['assert_value'][0].keys():
            case['url'] = url_value_result(case['url'], case['assert_value'][0])
        elif type(case['assert_value'][0]) is dict:
            case['data'] = many_data_result(case['data'], case['assert_value'][0])

    if 'random' in case['env'].keys():
        case['data'] = data_value_replace(case['env']['random'], case['data'])
    elif 'randompath' in case['env'].keys():
        case['url'] = data_number_replace(case['env']['randompath'], case['url'])

    for i in range(num):
        msg = 'start{},这是第{}遍——执行第{}条用例:{}'.format(datetime.datetime.now(), i, case['id'], case['case_name'])
        result.append(loop.run_until_complete(hello(case, msg, i)))
    # print(result)
    time_data = assert_time(case, result)

    time_sum = time_number(time_data)
    return time_sum


#  执行方案
def func (num, msg, ii):
    # 打印出来接口返回时间
    try:
        since = datetime.datetime.now()
        result = httpRequest().httpGet(num['url'], num['method'], eval(num['data']), num['sql'], num['env'])
        # result = requests.get(num['url'],eval(num['data']),).json()
        time_elapsed = datetime.datetime.now() - since
        logger.info('{},start{},Testing complete in {}s'.format(msg, since, time_elapsed.total_seconds()))
        result_dict = {'id': ii, 'result': result, 'time_elapsed': time_elapsed.total_seconds()}
    except:
        result_dict = {'id': ii, 'result': {'code': 1, 'result': ''}, 'time_elapsed': 0}

    return result_dict


# 开多进程，pool表示进程数，num表示子进程数
def property (case, pool, num):
    result = []
    if type(case['assert_value']) is dict:
        if type(case['assert_value'][0]) is dict and 'id' in case['assert_value'][0].keys():
            case['data'] = data_value_result(case['data'], case['assert_value'])
        elif type(case['assert_value'][0]) is dict and 'idlist' in case['assert_value'][0].keys():
            case['data'] = idlist_value_result(case['data'], case['assert_value'][0])
        elif type(case['assert_value'][0]) is dict and 'path' in case['assert_value'][0].keys():
            case['url'] = url_value_result(case['url'], case['assert_value'][0])
        elif type(case['assert_value'][0]) is dict:
            case['data'] = many_data_result(case['data'], case['assert_value'][0])

    if 'random' in case['env'].keys():
        case['data'] = data_value_replace(case['env']['random'], case['data'])
    elif 'randompath' in case['env'].keys():
        case['url'] = data_number_replace(case['env']['randompath'], case['url'])

    pool = multiprocessing.Pool(processes=pool)
    for ii in range(num):
        print('start{}'.format(datetime.datetime.now()))
        msg = 'start{},这是第{}遍——执行第{}条用例:{}'.format(datetime.datetime.now(), ii, case['id'], case['case_name'])
        # result.append(pool.apply(func, (case, msg, ii)))          # 同步执行
        result.append(pool.apply_async(func, (case, msg, ii)))  # 异步执行
    pool.close()
    pool.join()
    result_time = []
    for res in result:
        result_time.append(res.get())
    time_data = assert_time(case, result_time)

    time_sum = time_number(time_data)
    return time_sum


def assert_time (case, result_time):
    result_data = []
    for i in range(len(result_time)):
        result_dict = {}
        result_dict['id'] = result_time[i]['id']
        result_dict['time'] = result_time[i]['time_elapsed']
        result_dict['code'] = result_time[i]['result']['code']

        value = result_time[i]['result']['code']
        if len(case['assert_value']) != 0 and type(case['assert_value']) is list:
            value = assert_value_result(result_time[i]['result'], case['assert_value'][0])
        elif len(case['assert_value']) > 1:
            value = assert_value_result(result_time[i]['result'], case['assert_value'][1])
        try:
            # 断言对比(期望值，实际返回值)
            assert case['code'] == str(value)
            result_dict['result'] = 'pass'
            if 'my_sql' in case['sql'].keys():
                sql_result = getMysqlInfo(projectenv[1]).get_mysql_info(case['sql']['my_sql'],
                                                                        case['sql']['condition'],
                                                                        case['sql']['code'])
                try:
                    assert sql_result[0] == case['sql']['result']
                    result_dict["sql_result"] = 'pass'
                except Exception as e:
                    result_dict["sql_result"] = 'fail'
                    # t.write_Excel(id + 1, result_dict)
                    raise e

            else:
                result_dict["sql_result"] = 'pass'

        except Exception as e:
            result_dict['result'] = 'fail'
            result_dict["sql_result"] = 'fail'
            # t.write_Excel(id + 1, result_dict)
            raise e

        # t.write_Excel(id + 1, result_dict)
        result_data.append(result_dict)
    return result_data


def time_number (data):
    time_list = []
    passsum = 0
    for i in range(len(data)):
        time_list.append(data[i]['time'])
        if data[i]['result'] == 'pass':
            passsum += 1
    array_max = np.max(time_list)
    array_min = np.min(time_list)
    array_sum = format(np.sum(time_list), '.6f')
    array_mean = format(eval(array_sum) / len(data), '.6f')
    fail_sum = format(1 - (passsum / len(data)), '.2f')

    # print(time_list, array_max, array_min, array_sum, array_mean, fail_sum)  # 返回array最大值位置
    time_data = {'timemax': array_max, 'timemin': array_min, 'timesum': array_sum, 'timemean': array_mean,
                 'failsum': fail_sum}
    return time_data


if __name__ == "__main__":
    data = {'id': 247, 'case_name': '企业直销-家属套餐详情',
            'url': 'http://management-fed-gray.helianhealth.com/envk8s/healthmanage-web/app/marketV2/goodsPkg/detail',
            'method': 'GET', 'sql': {},
            'data': '{"uid":"32","spuId":"14651","enterpriseUserCardId":"128","useType":"4"}', 'code': '0', 'env': {},
            'assert_value': []}

    print(run_test(data, 20, 100))
