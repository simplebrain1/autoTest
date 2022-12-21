# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import uiautomator2 as u2

from autoTestScripts.python.base_test import BaseTestCase
from autoTestScripts.python.test_cold_boot_time_home import TestHomeColdBootTime
from autoTestScripts.python.test_cold_boot_time_home_header_news import TestHomeHeaderNewsClickBootTime
from autoTestScripts.python.test_cold_boot_time_home_history import TestHomeHistoryClickBootTime
from autoTestScripts.python.test_cold_boot_time_home_movie_detail import TestHomeDetailClickBootTime
from autoTestScripts.python.test_cold_boot_time_home_search import TestHomeSearchClickBootTime


def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。


def test_single(test_cls: BaseTestCase):
    test = test_cls(d)  # 创建测试对象
    test.test_case()  # 开始测试
    d.sleep(20)


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    # print_hi('PyCharm')
    d = u2.connect()
    test_single(TestHomeColdBootTime)
    test_single(TestHomeHeaderNewsClickBootTime)
    test_single(TestHomeHistoryClickBootTime)
    test_single(TestHomeDetailClickBootTime)
    test_single(TestHomeSearchClickBootTime)
