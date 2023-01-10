# 批量执行自动化示例脚本。
import os
import time

import uiautomator2 as u2

from autoTestScripts.python.base_test import BaseTestCase
from autoTestScripts.python.scriptUtils import utils
from test_softsetting_boot_time import TestSoftSettingBootTime
from test_softsettings_view_hierarchy import TestSoftSettingUiHierarchy

PATH = lambda p: os.path.abspath(p)


def test_single(test_cls: BaseTestCase, test_num=1):
    """单独测某一个案例"""
    all_test_success = True
    for i in range(test_num):
        test_cls.setup()
        ret = test_cls.test_case()  # 开始测试
        d.sleep(5)  # 休眠5s
        if not ret:
            all_test_success = False
            break
    return all_test_success


def auto_install_app(apk_name):  # 自动安装本地apk
    path = PATH("{}/{}/".format(os.getcwd(), "localApks"))
    path_apk = PATH("{}/{}".format(path, apk_name))
    print(path_apk)
    print(os.path.exists(path_apk))
    if os.path.exists(path_apk):
        d.app_install(path_apk)
    print("auto_install_app end")


# 低端
if __name__ == '__main__':
    start_test = time.time()
    print("merge test start {}".format(start_test))
    local_apk_name = "SimpleLauncher.apk"
    d = u2.connect(utils.get_serial_num())
    # auto_install_app(local_apk_name)
    count = 3  # 测试次数
    test_single(TestSoftSettingBootTime(d, standard_value=3, splash_standard_value=1), test_num=count)
    # 低端机冷启动最后测试热启动时可能还是冷启动
    test_single(TestSoftSettingBootTime(d, "hot", standard_value=1), test_num=count)
    # UI层级只需要测试一次
    test_single(TestSoftSettingUiHierarchy(d), test_num=1)

    print("merge test start {}".format(time.time() - start_test))