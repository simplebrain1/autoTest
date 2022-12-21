#!/usr/bin/env python
# -*- coding: utf-8 -*-


import threading

import uiautomator2 as u2

from autoTestScripts.python.pages.home_page import HomePage
from base_test import BaseTestCase
from scriptUtils import file_uitls

"""
主页向下切内容帧信息TestCase
执行完脚本，自动操作并在目前下/FpsFiles/homeContent/下生成对应的帧数据文件fps_temp.txt
"""


class TestHomeContentSwitch(BaseTestCase):

    def setup(self):
        self.tag = "主页向下切内容测试"
        print("you are testing apk is :" + self.current_pkg + " ,apk_cls:" + self.current_cls + ",tag:" + self.tag)

        self.save_file_name = "homeContent"
        self.enable_record = False
        self.home = HomePage(self.d)
        # self.timeout = 180  # 测试的时间
        print("  timeout {}".format(self.timeout))

    def run(self, total):
        if self.version > 23:
            cmd = "sh /data/local/tmp/fps_info.sh {0} {1} {2}".format(total, "/data/local/tmp/" + self.save_file_name,
                                                                      self.home.target_pkg)
        else:
            cmd = "sh /data/local/tmp/fps_info.sh {0} {1} {2} {3}".format(total,
                                                                          "/data/local/tmp/" + self.save_file_name,
                                                                          self.home.target_pkg + "/" + self.home.target_cls + "#0",
                                                                          "1")
        # utils.shell(cmd).wait()
        self.d.shell(cmd, timeout=total)
        print("run test end {}".format(cmd))
        self.test_completion.set()

    def test_action(self):
        print("testHomeContentSwitch is start")
        has_tool = file_uitls.push_fpstool_to_device(self)
        if not has_tool:
            return
        t = threading.Thread(target=self.run, args=(self.timeout,))
        t.start()
        self.home.monitor_home_content(self.timeout)
        self.d.sleep(1)
        file_uitls.move_fps_data_to_save(self, self.save_file_name)
        print("testHomeContentSwitch is end")


if __name__ == "__main__":
    d = u2.connect()  # 连接设备
    test = TestHomeContentSwitch(d)  # 创建测试对象
    test.setup()  # 初始化
    test.test_case()  # 开始测试
