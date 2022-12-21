#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

import uiautomator2 as u2

from autoTestScripts.python.pages.home_page import HomePage
from autoTestScripts.python.scriptUtils import file_uitls
from base_test import BaseTestCase

"""主页切Tab时长视频录制TestCase"""
PATH = lambda p: os.path.abspath(p)


class TestHomeTabSwitchTime(BaseTestCase):
    def setup(self):
        self.tag = "切主页tab测试"
        print("you are testing apk is :" + self.current_pkg + " ,apk_cls:" + self.current_cls + ",tag:" + self.tag)
        self.save_file_name = "homeTabDelay"
        self.enable_record = True
        self.home = HomePage(self.d)

    def test_case_reset(self):
        self.home.init_view_state(self.home.init_start_view_tab)

    def test_action(self):
        print("TestHomeTabSwitchTime is start")
        duration = self.home.delay_time_home_tab()
        print("end send key {}".format(duration))
        file_uitls.write_to_csv(self.save_file_name, duration=str(duration), scan=self.tag)
        self.test_completion.set()
        print("TestHomeTabSwitchTime is end")


if __name__ == "__main__":
    d = u2.connect()
    test = TestHomeTabSwitchTime(d)  # 创建测试对象
    test.setup()  # 初始化
    test.test_case()  # 开始测试
