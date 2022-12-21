#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from autoTestScripts.python.pages.base_page import BasePage

"""主页搜索页场景类"""


class HomeSearchPage(BasePage):
    def __init__(self, device):
        super().__init__(device)
        self.apk_cls = '.SkySearchActivity'  # 类名
        self.home_search_show_view = "热搜推荐"
        self.home_search_content_show_view = "猜你想搜"

    def monitor_search_content(self):
        """模拟主页搜索页面搜索内容"""
        self.d.app_start("com.tianci.movieplatform", self.apk_cls, wait=True, stop=True)
        self.d.sleep(1)
        print("start search111 {}".format(time.time()))
        self.by_xpath(self.home_search_show_view).wait()
        print("start search {}".format(time.time()))
        time_start_search = time.time()
        self.d.press("center")
        view_show = self.d(text=self.home_search_content_show_view).wait(exists=True)
        print(view_show)
        if view_show:
            print("end search {}".format(time.time()))
            search_response_time = time.time() - time_start_search
            return round(search_response_time, 2)
        return -1
