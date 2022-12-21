#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from autoTestScripts.python.pages.home_page import HomePage

keyword = "right"

"""儿童教育首页场景类"""


class EducateHomePage(HomePage):
    def __init__(self, device):
        super().__init__(device)
        self.target_pkg = "com.coocaa.educate"
        self.target_cls_init = ".child.welcome.WelcomeGuideActivity"  # 儿童应用启动类
        self.target_cls = ".home.EduHomeActivity"  # 儿童模式展示类
        self.init_start_view_tab = "少儿"
        self.init_end_view_tab = "会员福利"
        self.init_start_view_content = "少儿"

    def monitor_home_content(self, timeout):
        """模拟儿童主页切内容"""
        global keyword
        self.d.app_start(self.target_pkg, self.target_cls_init, wait=True, stop=True)
        self.d.wait_activity(self.target_cls)
        view_start = self.by_xpath(self.init_start_view_content).wait()
        view_start_center = view_start.center()
        self.d.sleep(1)
        self.d.press("up")
        self.d.sleep(1)

        flag = False
        # 查找对应的tab
        while True:
            view = self.by_focused()
            if view is not None:
                view_txt = view.child(className="android.widget.TextView").get_text()
                if view_txt == self.init_start_view_content:
                    flag = True
                    break
                else:
                    self.d.press("right")
        if not flag:
            print("no find correct tab")
            return
        keyword = "down"
        deadline = time.time() + timeout
        while time.time() < deadline:
            view = self.by_focused()
            center_point = view.center()
            print(center_point)
            print(view_start.center())
            print(view_start_center == center_point)
            if self.div(80) <= center_point[0] <= self.div(657) and self.div(651) <= center_point[1] <= self.div(
                    974) or (int(deadline - time.time())) == (timeout / 2):
                keyword = "up"
            elif self.div(82) <= center_point[0] <= self.div(162) and self.div(129) <= center_point[1] <= self.div(
                    183) or view_start_center == center_point:
                keyword = "down"
            self.d.press(keyword)

    def monitor_home_tab(self, timeout=180):
        """模拟儿童主页切tab"""
        global keyword
        self.d.app_start(self.target_pkg, self.target_cls_init, wait=True, stop=True)
        self.d.wait_activity(self.target_cls)
        self.by_xpath(self.init_start_view_tab).wait().click()
        self.d.sleep(2)

        keyword = "right"
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.d.press(keyword)
            self.d.sleep(0.3)

    def watch_tab(self, orientation="H"):
        """儿童首页home持续切tab动作监听"""
        global keyword
        self.d.wait_activity(self.target_cls)
        print("EducateHomePage run {}".format(time.time()))
        view = self.by_focused()
        view_child = view.child(className="android.widget.TextView")
        if not view.exists or not view_child.exists:
            print("view is not exist")
            return
        try:
            if view_child is None:
                print("view txtChild is not exist")
                return
            if keyword == "right":
                text_focus = view_child.get_text()
            elif keyword == "left":
                text_focus = view_child.get_text()
            print("text_focus {}".format(text_focus))
            if text_focus == self.init_end_view_tab:
                if keyword == "right":
                    keyword = "left"
            if text_focus == self.init_start_view_tab:
                if keyword == "left":
                    keyword = "right"
        except Exception as e:
            raise e
