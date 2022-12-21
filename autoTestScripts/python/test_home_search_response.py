#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

import uiautomator2 as u2

from autoTestScripts.python.pages.home_search_page import HomeSearchPage
from autoTestScripts.python.scriptUtils import file_uitls
from base_test import BaseTestCase

"""在搜索页面，输入不同字母响应时间，例如输入R，右测内容页全显示视频录制TestCase"""
PATH = lambda p: os.path.abspath(p)


class TestHomeSearchContentResponseTime(BaseTestCase):
    def setup(self):
        self.tag = '搜索响应'  # 测试名称
        print("you are testing apk is :" + self.current_pkg + " ,apk_cls:" + self.current_cls + ",tag:" + self.tag)
        self.save_file_name = "TestHomeSearchContentResponseTime"
        self.home_search = HomeSearchPage(self.d)
        self.enable_record = True

    def test_action(self):
        print("TestHomeSearchContentResponseTime is start")
        duration = self.home_search.monitor_search_content()
        print("start search content time {}".format(duration))
        file_uitls.write_to_csv(self.save_file_name, duration=str(duration), scan=self.tag)
        self.test_completion.set()
        print("TestHomeSearchContentResponseTime is end")


if __name__ == "__main__":
    d = u2.connect()
    test = TestHomeSearchContentResponseTime(d)  # 创建测试对象
    test.setup()  # 初始化
    test.test_case()  # 开始测试
