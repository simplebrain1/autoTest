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


class TestLocalMediaBootTime(BaseTestCase):
    def setup(self):
        self.tag = '打开本地媒体'
        print("you are testing apk is :" + self.current_pkg + " ,apk_cls:" + self.current_cls + ",tag:" + self.tag)
        self.save_file_name = "TestLocalMediaBootTime"
        self.home = HomePage(self.d)
        self.enable_record = True
        self.enable_auto_analyse = True
        self.target_boot_pkg = "com.tianci.localmedia"
        self.target_show_view = "我的设备"

    def test_case_reset(self):
        self.home.cold_boot_time_app_reset(self.target_boot_pkg)

    def test_action(self):
        print("TestLocalMediaBootTime is start")
        duration = self.home.cold_boot_time_app(self.target_show_view)
        print("start target Activity time {}".format(duration))
        file_uitls.write_to_csv(self.save_file_name, duration=str(duration), scan=self.tag)
        self.test_completion.set()
        print("TestLocalMediaBootTime is end")

    def calculate_video_time(self, _result_get: ClassifierResult):
        path_stagesepx_with_keras_dir = PATH("%s/%s" % (os.getcwd(), self.stagesepx_with_keras_dir))
        picture_for_train_path = "%s/picture_for_train/%s" % (path_stagesepx_with_keras_dir, self.save_file_name)
        splash_image_path = "%s/splash.png" % picture_for_train_path
        main_page_image_path = "%s/main_page.png" % picture_for_train_path
        cost_time_splash = round(stagesepx_utils.calculate_splash(_result_get, "-3", "3",
                                                                  splash_image_path,
                                                                  {'mse': 1, 'ssim': 0.97, 'pnsr': 10}
                                                                  ), 2)  # 自动计算视频帧中的闪屏页时间
        cost_time_ui_showed = round(stagesepx_utils.calculate_ui_showed(_result_get, "-3", "6",
                                                                        main_page_image_path,
                                                                        {'mse': 10.0, 'ssim': 0.97, 'pnsr': 10}
                                                                        ), 2)  # 自动计算视频帧中的ui完全显示时间
        file_uitls.write_to_csv(self.save_file_name,
                                self.stagesepx_result_dir, duration=str(cost_time_ui_showed), scan=self.tag)


if __name__ == "__main__":
    d = u2.connect()
    test = TestLocalMediaBootTime(d)  # 创建测试对象
    test.setup()  # 初始化
    test.test_case()  # 开始测试
