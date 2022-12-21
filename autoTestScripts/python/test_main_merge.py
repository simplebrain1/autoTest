# 批量执行自动化示例脚本。

import time

import uiautomator2 as u2

from autoTestScripts.python.base_test import BaseTestCase
from autoTestScripts.python.test_cold_boot_time_home import TestHomeColdBootTime
from autoTestScripts.python.test_cold_boot_time_home_header_news import TestHomeHeaderNewsClickBootTime
from autoTestScripts.python.test_cold_boot_time_home_history import TestHomeHistoryClickBootTime
from autoTestScripts.python.test_cold_boot_time_home_movie_detail import TestHomeDetailClickBootTime
from autoTestScripts.python.test_cold_boot_time_home_myapp import TestHomeMyappClickBootTime
from autoTestScripts.python.test_cold_boot_time_home_search import TestHomeSearchClickBootTime
from autoTestScripts.python.test_cold_boot_time_start_softsettings import TestSoftSettingClickBootTime
from autoTestScripts.python.test_delay_time_home_tab_switch import TestHomeTabSwitchTime
from autoTestScripts.python.test_home_content_switch import TestHomeContentSwitch
from autoTestScripts.python.test_home_search_response import TestHomeSearchContentResponseTime
from autoTestScripts.python.test_home_tab_switch import TestHomeTabSwitch
from autoTestScripts.python.test_hot_boot_time_home import TestHomeHotBootTime
from autoTestScripts.python.test_time_voice_show import TestVoiceTipShowTime


def test_single(test_cls: BaseTestCase, test_num=1):
    """单独测某一个案例"""
    for i in range(test_num):
        test = test_cls(d)  # 创建测试对象
        test.setup()
        ret = test.test_case()  # 开始测试
        d.sleep(5)  # 休眠5s
        if ret:
            continue
    return ret


# 批量运行自动化测试案例（以主页为例）
if __name__ == '__main__':
    start_test = time.time()
    print("merge test start {}".format(start_test))
    d = u2.connect()
    count = 2  # 测试次数
    test_single(TestHomeColdBootTime, test_num=count)
    test_single(TestHomeHeaderNewsClickBootTime, test_num=count)
    test_single(TestHomeHistoryClickBootTime, test_num=count)
    test_single(TestHomeDetailClickBootTime, test_num=count)
    test_single(TestHomeMyappClickBootTime, test_num=count)
    test_single(TestHomeSearchClickBootTime, test_num=count)
    test_single(TestSoftSettingClickBootTime, test_num=count)
    test_single(TestHomeTabSwitchTime, test_num=count)
    test_single(TestHomeSearchContentResponseTime, test_num=count)
    test_single(TestHomeHotBootTime, test_num=count)
    test_single(TestVoiceTipShowTime, test_num=count)

    # # 主页帧率自动化数据采集
    test_single(TestHomeContentSwitch, test_num=count)

    # for i in range(1):
    test_single(TestHomeTabSwitch, test_num=count)
    print("merge test start {}".format(time.time() - start_test))
