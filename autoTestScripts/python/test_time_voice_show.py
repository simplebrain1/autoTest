#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import time

import uiautomator2 as u2

from autoTestScripts.python.scriptUtils import file_uitls, utils
from base_test import BaseTestCase

"""小维AI呼出时长"""
PATH = lambda p: os.path.abspath(p)


class TestVoiceTipShowTime(BaseTestCase):
    def setup(self):
        self.tag = '小维AI呼出时长'
        print("you are testing apk is :" + self.current_pkg + " ,apk_cls:" + self.current_cls + ",tag:" + self.tag)
        self.save_file_name = "TestVoiceTipShowTime"
        self.enable_record = True

    def test_action(self):
        print("TestVoiceTipShowTime is start")
        start_time_voice = time.time()
        print("start_time_voice:".format(start_time_voice))
        utils.shell("am broadcast -a com.skyworth.angel.voice.textinput --es input 小维小维").wait()
        view_show = self.d.xpath("小维小维").wait(timeout=10)
        print(view_show)
        if view_show is not None:
            duration = round(time.time() - start_time_voice, 2)
            print("start target Activity time {}".format(duration))
            file_uitls.write_to_csv(self.save_file_name, duration=str(duration), scan=self.tag)
        self.test_completion.set()
        print("TestVoiceTipShowTime is end")


if __name__ == "__main__":
    d = u2.connect()
    test = TestVoiceTipShowTime(d)  # 创建测试对象
    test.setup()  # 初始化
    test.test_case()  # 开始测试
