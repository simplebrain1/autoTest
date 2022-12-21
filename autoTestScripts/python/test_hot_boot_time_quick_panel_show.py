#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

import uiautomator2 as u2

from autoTestScripts.python.pages.home_page import HomePage
from autoTestScripts.python.scriptUtils import file_uitls
from base_test import BaseTestCase

"""主页菜单键调出便捷面版"""
PATH = lambda p: os.path.abspath(p)


class TestQuickPanelHotBootTime(BaseTestCase):
    def setup(self):
        self.tag = '便捷面版热启动'
        print("you are testing apk is :" + self.current_pkg + " ,apk_cls:" + self.current_cls + ",tag:" + self.tag)
        self.save_file_name = "TestQuickPanelHotBootTime"
        self.home = HomePage(self.d)
        # self.enable_record = True

    def test_action(self):
        print("TestQuickPanelHotBootTime is start")
        duration = self.home.boot_time_quick_panel_show(is_play_scene=False)
        print("start target Activity time {}".format(duration))
        file_uitls.write_to_csv(self.save_file_name, duration=str(duration), scan=self.tag)
        self.test_completion.set()
        print("TestQuickPanelHotBootTime is end")


if __name__ == "__main__":
    d = u2.connect()
    test = TestQuickPanelHotBootTime(d)  # 创建测试对象
    test.setup()  # 初始化
    test.test_case()  # 开始测试
