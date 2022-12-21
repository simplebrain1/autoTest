#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

import uiautomator2 as u2

from autoTestScripts.python.pages.home_page import HomePage
from autoTestScripts.python.scriptUtils import file_uitls
from base_test import BaseTestCase

"""主页冷启动界面时长视频录制TestCase"""
PATH = lambda p: os.path.abspath(p)


class TestHomeDetailClickBootTime(BaseTestCase):
    def setup(self):
        self.tag = '打开影视详情页'
        print("you are testing apk is :" + self.current_pkg + " ,apk_cls:" + self.current_cls + ",tag:" + self.tag)
        self.save_file_name = "TestHomeDetailClickBootTime"
        self.home = HomePage(self.d)
        self.enable_record = True

    def test_case_reset(self):
        self.home.cold_boot_time_home_view_click_reset(self.home.home_movie_detail_click_tab)

    def test_action(self):
        print("TestHomeDetailClickBootTime is start")
        duration = self.home.cold_boot_time_home_view_click(self.home.home_movie_detail_click_view,
                                                            self.home.home_movie_detail_show_view)
        print("start target Activity time {}".format(duration))
        file_uitls.write_to_csv(self.save_file_name, duration=str(duration), scan=self.tag)
        self.test_completion.set()
        print("TestHomeDetailClickBootTime is end")


if __name__ == "__main__":
    d = u2.connect()
    test = TestHomeDetailClickBootTime(d)  # 创建测试对象
    test.setup()  # 初始化
    test.test_case()  # 开始测试
