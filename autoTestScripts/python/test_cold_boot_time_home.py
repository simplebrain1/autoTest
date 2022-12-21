#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import uiautomator2 as u2
from stagesepx.classifier import ClassifierResult

from autoTestScripts.python.pages.home_page import HomePage
from autoTestScripts.python.scriptUtils import file_uitls, stagesepx_utils
from base_test import BaseTestCase

"""主页冷启动界面时长视频录制TestCase"""
PATH = lambda p: os.path.abspath(p)


class TestHomeColdBootTime(BaseTestCase):
    def setup(self):
        self.tag = '主页home冷启动'
        print("you are testing apk is :" + self.current_pkg + " ,apk_cls:" + self.current_cls + ",tag:" + self.tag)
        self.save_file_name = "TestHomeColdBootTime"
        self.time_before_record = 0
        self.enable_record = True
        self.enable_auto_analyse = False
        self.home = HomePage(self.d)

    def test_action(self):
        print("TestHomeColdBootTime is start")
        self.d.sleep(1)
        duration = self.home.cold_boot_time_home(self.home.home_myapp_click_view)
        print("start target Activity time {}".format(duration))
        file_uitls.write_to_csv(self.save_file_name, duration=str(duration), scan=self.tag)
        self.test_completion.set()
        print("TestHomeColdBootTime is end")

    def calculate_video_time(self, _result_get: ClassifierResult):
        cost_time = round(stagesepx_utils.calculate(_result_get, "1", "3"), 2)  # 自动计算视频帧中的时间
        file_uitls.write_to_csv(self.save_file_name, self.stagesepx_result_dir, duration=str(cost_time), scan=self.tag)


if __name__ == "__main__":
    d = u2.connect()
    test = TestHomeColdBootTime(d)  # 创建测试对象
    test.setup()  # 初始化
    test.test_case()  # 开始测试
