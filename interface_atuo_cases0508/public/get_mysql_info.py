# -*- coding: utf-8 -*-
# @Author  : zgh
# @Email   : 849080458@qq.com
# @File    : manage.py
# @Software: PyCharm

from public.config import config
import pymysql
from conf import Allpath
from public.logger import Log
import time

logger = Log('get_mysql_info', Allpath.log_path)
data_t = time.strftime('%Y-%m-%d')
test_db = config().read_config(Allpath.db_conf_path, 'DBCONFIG', 'config_case_db')


class getMysqlInfo:
    def __init__(self, db):
        # 传入参数：路径、便签、对象
        self.config = db
        logger.info("本次数据库调用配置成功！")

    def get_cnn (self):
        # 出入获取的配置文件，建立游标
        cnn = pymysql.connect(**self.config)
        return cnn

    def auto_insert (self):
        list_1 = {}
        cnn = self.get_cnn()
        cursor = cnn.cursor()
        # 执行SQL语句
        cur = cursor.execute("select * from autotest.jkgl")
        # 查看数据库数据
        data = cursor.description
        data_1 = []
        test = []
        for i in range(len(data)):
            data_1.append(data[i][0])
            # print(data[i][0])
            test.append('%(' + data[i][0] + ')s')  # 生成value数列
            list_1[data[i][0]] = ''
        table_sql = "INSERT INTO jkgl (" + ','.join(data_1) + ")" + " VALUES " + "(" + ','.join(test) + ")"
        logger.info("插入数据库sql拼接成功！%s" % table_sql)
        return table_sql

    def Instert_mysql (self, data):
        sql = getMysqlInfo(test_db).auto_insert()
        cnn = self.get_cnn()
        cursor = cnn.cursor()
        try:
            # 传入sql语句，对应字段值
            cursor.executemany(sql, data)
            cnn.commit()
            logger.info('sql写入统计测试记录成功！')
        except Exception as e:
            logger.error('sql写入统计测试记录失败！！！%s' % e)
            raise e
        cnn.close()

    def get_mysql_info (self, my_sql, condition, code):
        cnn = self.get_cnn()
        cursor = cnn.cursor()
        # 传入sql语句，对应字段值
        cursor.execute(my_sql, (condition,))
        desc = cursor.description  # 获取字段的描述，默认获取数据库字段名称，重新定义时通过AS关键重新命名即可
        if code == 1:  # 查询所有的
            result = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
        else:
            # 查询一条信息
            result = cursor.fetchone()  # print(result)
        cnn.close()
        logger.info("查询数据库调用成功！{}".format(result))
        return result

    def del_cardid_info(self):
        sql1 = "UPDATE `hospital_user_card` SET isdelete=1 WHERE user_name like '小七%' and `status` != 0 and modify_time <='" + data_t + " 23:59:59'; "
        sql2 = "UPDATE `enterprise_user_card` SET is_deleted=1 WHERE user_name like '小七%' AND begin_time <='" + data_t + " 23:59:59'; "
        sql3 = "delete from msg_content where mobile_no in ('17681829051','15258814180'); "
        sql4 = "UPDATE `hospital_company` SET isdelete=1 WHERE station_id in ('HL99998','HL99997') and company_name like '接口测试%' AND create_time <='" + data_t + " 23:59:59'; "
        sql5 = "UPDATE `market_coupon_template` SET coupon_status=1 where coupon_name ='接口校验' or coupon_name ='接口优惠券';"
        # sql6 = "update `health_user_report_detail` set is_delete = '1' where user_id = '自主上传';"
        cnn = self.get_cnn()
        cursor = cnn.cursor()
        # 传入sql语句，对应字段值
        cursor.execute(sql1)
        cursor.execute(sql2)
        cursor.execute(sql3)
        cursor.execute(sql4)
        cursor.execute(sql5)
        # cursor.execute(sql6)
        cnn.commit()
        result = cursor.fetchone()
        cursor.close()
        return result

    def get_mysql_info_test (self, my_sql, code):
        cnn = self.get_cnn()
        cursor = cnn.cursor()
        # 传入sql语句，对应字段值
        cursor.execute(my_sql)
        desc = cursor.description  # 获取字段的描述，默认获取数据库字段名称，重新定义时通过AS关键重新命名即可
        if code == 1:  # 查询所有的
            data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]  # 列表表达式把数据组装起来
        elif code == 0:  # 查询一条信息
            data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchone()]  # 列表表达式把数据组装起来
        cnn.close()
        # print(data_dict)
        result = {'restult': "", 'sum': '', 'ok': '', 'fail': '', 'error': '', 'error_1': ''}
        result['restult'] = data_dict[0]['restult']

        sum = []
        ok = []
        fail = []
        error = []
        error_1 = []
        for i in range(1, len(data_dict) + 1):
            ii = len(data_dict) - i
            sum.append(data_dict[ii]['sum'])
            ok.append(data_dict[ii]['ok'])
            fail.append(data_dict[ii]['fail'])
            error.append(data_dict[ii]['error'])
            error_1.append(data_dict[ii]['error_1'])
        result['sum'] = sum
        result['ok'] = ok
        result['fail'] = fail
        result['error'] = error
        result['error_1'] = error_1
        # print(result)
        logger.info("测试结果数据库调用成功！{}".format(result))
        return result

    # 微医全退款和部分退款,weiyi后的代表金额，分
    def update_weiyi_refund(self, env):
        cnn = self.get_cnn()
        cursor = cnn.cursor()
        # 传入sql语句，对应字段值
        my_sql = "UPDATE `weiyi_order_history` SET order_status='7',refund_amount='" + str(env[
                                                                                               'weiyi']) + "'  WHERE  update_time in(SELECT * from (select MAX(update_time) time from weiyi_order_history where order_status ='6') a );"
        cursor.execute(my_sql)
        cnn.commit()
        cnn.close()


if __name__ == '__main__':
    # db =config().read_config(Allpath.db_conf_path, 'DBCONFIG', 'config_b2h')
    # sql_result = getMysqlInfo(db).update_weiyi_refund()

    # sql = {"my_sql": "select msg_content from `msg_send_log` where mobile_no in ('13429666593','17681829051','15258814180') and msg_content like '%%小七%%' ORDER BY id DESC LIMIT %s;", "condition": 3, "code": 0,'result':"【禾连健康】接口测试2021-02-25 14-29-15的客户小七2，贵单位体检开始线上预约啦！请登录体检预约系统完成预约后再体检，预约方式：关注“禾健康企业服务号”点击“团检预约”开启体检服务。","sql":0}
    #
    # sql_result = getMysqlInfo(test_db).get_mysql_info(sql['my_sql'], sql['condition'],sql['code'])
    # data = [{
    #     'restult': "{'testname': '质量保障部—章广华', 'time': '2019-11-11 11:55:14', 'sumtime': '0:00:00.125677', 'testresult': '共 1 条接口用例，错误 1 条', 'tonggl': '0.00%'}",
    #     'sum': 1, 'ok': 0, 'fail': 0, 'error': 1, 'error_1': '100.00%', 'date': '2019-11-11_11_55_13'}]
    # sql_result = getMysqlInfo(projectenv[1]).Instert_mysql(data)
    # sql_result=getMysqlInfo(projectenv[2]).get_mysql_info_test("select * from znkf ORDER BY date DESC LIMIT 10;",1)
    # sql = getMysqlInfo(projectenv[2]).auto_insert()
    # print(db,sql_result)
    getMysqlInfo(config().read_config(Allpath.db_conf_path, 'DBCONFIG', 'config_b2h')).del_cardid_info()
