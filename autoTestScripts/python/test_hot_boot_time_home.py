#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

import uiautomator2 as u2

from autoTestScripts.python.pages.home_page import HomePage
from autoTestScripts.python.scriptUtils import file_uitls
from base_test import BaseTestCase

"""主页热启动界面时长视频录制TestCase"""
PATH = lambda p: os.path.abspath(p)


class TestHomeHotBootTime(BaseTestCase):
    def setup(self):
        self.tag = '主页home热启动'
        print("you are testing apk is :" + self.current_pkg + " ,apk_cls:" + self.current_cls + ",tag:" + self.tag)
        self.save_file_name = "TestHomeHotBootTime"
        self.home = HomePage(self.d)
        self.enable_record = True
        self.record_timeout = 30

    def test_action(self):
        print("TestHomeHotBootTime is start")
        # try:
        duration = self.home.hot_boot_time_home(self.home.home_myapp_click_view)
        print("start target Activity time {}".format(duration))
        file_uitls.write_to_csv(self.save_file_name, duration=str(duration), scan=self.tag)
        self.test_completion.set()
        print("TestHomeHotBootTime is end")
        # except Exception as e:
        #     print("TestHomeHotBootTime is exception!" + e)
        #     raise e


if __name__ == "__main__":
    d = u2.connect()
    test = TestHomeHotBootTime(d)  # 创建测试对象
    test.setup()  # 初始化
    test.test_case()  # 开始测试
