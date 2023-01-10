#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import uiautomator2 as u2
from stagesepx.classifier import ClassifierResult

from autoTestScripts.python.pages.home_page import HomePage
from autoTestScripts.python.scriptUtils import file_uitls, stagesepx_utils, utils
from autoTestScripts.python.base_test import BaseTestCase

"""主页冷启动界面时长视频录制TestCase"""
PATH = lambda p: os.path.abspath(p)


class TestSoftSettingBootTime(BaseTestCase):
    def __init__(self, device: u2.Device, test_type: str = "cold", standard_value: int = 2,
                 splash_standard_value: float = 0.8
                 ):
        super(TestSoftSettingBootTime, self).__init__(device)
        self.test_type = test_type
        self.standard_value = standard_value
        self.splash_standard_value = splash_standard_value

    def setup(self):
        self.tag = '打开系统设置'
        print("you are testing apk is :" + self.current_pkg + " ,apk_cls:" + self.current_cls + ",tag:" + self.tag)
        if self.test_type == "cold":
            self.save_file_name = "TestSoftSettingClickBootTime"
            self.tag_cn = '设置冷启动'
        elif self.test_type == "hot":
            self.save_file_name = "TestSoftSettingHotBootTime"
            self.tag_cn = '设置热启动'
        self.stagesepx_model_file_name = "TestSoftSettingClickBootTime"
        self.home = HomePage(self.d)
        self.enable_record = True
        self.enable_auto_analyse = True
        self.target_boot_pkg = "com.coocaa.os.softsettings"
        self.target_show_view = "常规"
        self.stagesepx_with_keras_dir = "../../stagesepx_with_keras"

    def test_case_reset(self):
        if self.test_type == "cold":
            self.home.cold_boot_time_app_reset(self.target_boot_pkg)
        elif self.test_type == "hot":
            self.home.hot_boot_time_app_reset(self.target_boot_pkg)

    def test_action(self):
        print("TestSoftSettingClickBootTime is start")
        duration = self.home.cold_boot_time_app(self.target_show_view)
        print("start target Activity time {}".format(duration))
        file_uitls.save_app_perf_data(self.save_file_name,
                                      app_info=self.d.app_info(self.target_boot_pkg),
                                      standard_value=self.standard_value,
                                      test_type="应用启动时间",
                                      test_subcategories=str(self.tag_cn),
                                      test_content=str(self.tag_cn),
                                      test_result=duration,
                                      comment="控件识别"
                                      )
        self.test_completion.set()
        print("TestSoftSettingClickBootTime is end")

    def calculate_video_time(self, _result_get: ClassifierResult):
        path_stagesepx_with_keras_dir = PATH("%s/%s" % (os.getcwd(), self.stagesepx_with_keras_dir))
        picture_for_train_path = "%s/picture_for_train/%s" % (path_stagesepx_with_keras_dir,
                                                              self.stagesepx_model_file_name)
        splash_image_path = "%s/splash.png" % picture_for_train_path
        main_page_image_path = "%s/main_page.png" % picture_for_train_path
        # 注意简易桌面上面不能有滚动的东西：比如设备未激活，会干扰变动时间的识别
        cost_time_splash = round(stagesepx_utils.calculate_splash(_result_get, "-3", "2",
                                                                  splash_image_path,
                                                                  {'mse': 5, 'ssim': 0.97, 'pnsr': 10}
                                                                  ), 2)  # 自动计算视频帧中的闪屏页时间
        cost_time_ui_showed = round(stagesepx_utils.calculate_ui_showed(_result_get, "-3", "4",
                                                                        main_page_image_path,
                                                                        {'mse': 15.0, 'ssim': 0.97, 'pnsr': 10}
                                                                        ), 2)  # 自动计算视频帧中的ui完全显示时间
        file_uitls.write_to_csv(self.save_file_name, self.stagesepx_result_dir, duration=str(cost_time_ui_showed),
                                scan=self.tag)
        file_uitls.save_app_perf_data(self.save_file_name + "_stagesepx",
                                      app_info=self.d.app_info(self.target_boot_pkg),
                                      standard_value=self.standard_value,
                                      test_type="应用启动时间",
                                      test_subcategories=str(self.tag_cn),
                                      test_content=str(self.tag_cn),
                                      test_result=cost_time_ui_showed,
                                      comment="图像识别"
                                      )
        if self.test_type == "cold":
            file_uitls.save_app_perf_data(self.save_file_name + "_stagesepx",
                                          app_info=self.d.app_info(self.target_boot_pkg),
                                          standard_value=self.splash_standard_value,
                                          test_type="应用启动时间",
                                          test_subcategories="应用响应时间",
                                          test_content="设置响应时间",
                                          test_result=cost_time_splash,
                                          comment="图像识别"
                                          )


if __name__ == "__main__":
    d = u2.connect(utils.get_serial_num())
    test = TestSoftSettingBootTime(d)  # 创建测试对象
    test.setup()  # 初始化
    test.test_case()  # 开始测试
