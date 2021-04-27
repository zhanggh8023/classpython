# ————————————————
# @Time    : 2020/12/9 16:17
# @Author  : zgh
# @Email   : 849080458@qq.com
# @File    : LocustTest.py
# ————————————————


"""
创建后台管理站点压测类，需要继承TaskSet
可以添加多个测试任务
"""

from locust import HttpUser, TaskSet, task


"""
创建后台管理站点压测类，需要继承TaskSet
可以添加多个测试任务
"""
class AdminLoadTest(TaskSet):

    # 用户执行task前调用
    def on_start(self):
        pass

    # 用户执行task后调用
    def on_stop(self):
        pass

    @task
    def download(self):
        # 头部
        header = {"key":"value"}
        # 参数
        data = {"uid":"32","spuId":"14651","enterpriseUserCardId":"128","useType":"4"}
        self.client.get('/envk8s/healthmanage-web/app/marketV2/goodsPkg/detail',params=data,headers=header)

class RunLoadTests(HttpUser):
    """
    创建运行压测类
    """
    tasks = [AdminLoadTest]
    min_wait = 1000
    max_wait = 50000



if __name__ == "__main__":
    import os
    os.system("locust -f LocustTest.py --host=http://management-fed-gray.helianhealth.com --web-host=127.0.0.1")
