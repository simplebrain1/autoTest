#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from autoTestScripts.python.pages.base_page import BasePage

keyword = "right"

"""主页界面场景类"""


class HomePage(BasePage):
    def __init__(self, device):
        super().__init__(device)
        self.target_pkg = "com.tianci.movieplatform"
        self.target_cls = "com.coocaa.homepage.vast.HomePageActivity"
        self.init_start_view_content = "影视"
        self.init_start_view_content_show = "电影"
        self.init_start_view_tab = "AI互动"
        self.init_end_view_tab = "超高清"
        self.home_search_show_view = "热搜推荐"

        self.home_history_show_view = "视频"
        #   搜索定位标签，11月份主页用上面这个，9月19用下面这个
        # self.home_search_click_view = '//android.view.ViewGroup/android.widget.LinearLayout[1]/android.view.View[1]'
        self.home_search_click_view = '//*[@resource-id="android:id/content"]/android.widget.FrameLayout[' \
                                      '1]/android.widget.FrameLayout[4]/android.widget.FrameLayout[' \
                                      '1]/android.widget.LinearLayout[1]/android.view.View[1] '

        self.home_history_show_view = "视频"
        self.home_history_click_view = '历史 | 收藏'
        # '//android.support.v7.widget.RecyclerView/android.widget.FrameLayout[' \
        # '1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2] '

        self.home_myapp_show_view = "我的"  # '//android.support.v7.widget.RecyclerView/android.widget.FrameLayout[' \
        # '1]/android.widget.FrameLayout[1]'  # "我的"
        self.home_myapp_click_view = "我的应用"

        self.home_movie_detail_show_view = "全屏"
        self.home_movie_detail_click_tab = "影视"
        self.home_movie_detail_click_view = "//android.support.v7.widget.RecyclerView/android.widget.FrameLayout[" \
                                            "1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1] "
        self.home_header_news_show_view = "头条"
        self.home_header_news_click_view = '//android.support.v7.widget.RecyclerView/android.widget.FrameLayout[' \
                                           '1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[5] '
        self.home_tab_switch_view = '//android.support.v7.widget.RecyclerView/android.widget.FrameLayout[' \
                                    '1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[3] '

        self.home_quick_panel_show_view = '//*[@resource-id="android:id/content"]/android.widget.FrameLayout[' \
                                          '1]/android.widget.FrameLayout[2]/android.widget.FrameLayout[' \
                                          '1]/android.widget.LinearLayout[1] '

    def filter_ad(self):
        """过滤广告"""
        start_filter_time = time.time()
        exists = self.d(text=" 按【返回键】可关闭广告 | ").wait(timeout=8)  # 可能出现的广告界面
        print("exist {}".format(exists))
        if exists:
            self.d.press("back")
        cost_time = time.time() - start_filter_time
        return cost_time

    def monitor_home_content(self, timeout):
        """模拟主页切内容"""
        global keyword
        self.d.app_start(self.target_pkg, self.target_cls, wait=True, stop=True)
        self.d.wait_activity(self.target_cls)
        self.filter_ad()  # 过滤广告
        view_start = self.by_xpath(self.init_start_view_content).wait()
        view_start_center = view_start.center()
        # view_start.click()    #用这个定位焦点，应用有报停风险 （应用逻辑应该有问题）
        self.d(text="精选").click()

        flag = False
        while True:
            view = self.by_focused()
            if view is not None:
                view_child = view.child(className="android.widget.TextView")
                if view_child is not None:
                    view_txt = view_child.get_text()
                    if view_txt == self.init_start_view_content:
                        flag = True
                        break
                    else:
                        self.d.press("right")
        if not flag:
            print("no find correct tab")
            return
        self.d(text=self.init_start_view_content_show).wait(exists=True)
        keyword = "down"
        deadline = time.time() + timeout
        while time.time() < deadline:
            view = self.by_focused()
            center_point = view.center()
            print(center_point)
            print(view_start.center())
            print(view_start_center == center_point)
            if self.div(80) <= center_point[0] <= self.div(400) and self.div(600) <= center_point[1] <= self.div(
                    974) or (int(deadline - time.time())) == (timeout / 2):
                keyword = "up"
            elif self.div(857) <= center_point[0] <= self.div(1001) and self.div(107) <= center_point[1] <= self.div(
                    179) or view_start_center == center_point:
                keyword = "down"
            self.d.press(keyword)

    def monitor_home_tab(self, timeout=180):
        """模拟主页切tab"""
        print("monitor_home_tab")
        global keyword
        self.d.app_start(self.target_pkg, self.target_cls, wait=True, stop=True)
        self.d.wait_activity(self.target_cls)
        self.filter_ad()  # 过滤广告
        view = self.by_xpath(self.init_start_view_tab).wait()
        if view is not None:
            view.click()
        else:
            view = self.by_text(self.init_start_view_tab)
            view_show = view.wait(exists=True)
            if view_show:
                view.click()
        keyword = "right"
        deadline = time.time() + timeout
        while time.time() < deadline:
            view = self.by_focused()
            # center_point = view.center()
            # print(center_point)
            # if self.div(1606) <= center_point[0] <= self.div(1830) and self.div(107) <= center_point[1] <= self.div(
            #         179):
            #     keyword = "left"
            # elif self.div(50) <= center_point[0] <= self.div(230) and self.div(107) <= center_point[1] <= self.div(
            #         179):
            #     keyword = "right"
            view_child = view.child(className="android.widget.TextView")
            view_show = view.child(className="android.widget.TextView").wait(exists=True, timeout=2)
            if view_show:
                print(view_child.get_text())
                if self.init_end_view_tab == view_child.get_text():
                    keyword = "left"
                elif self.init_start_view_tab == view_child.get_text():
                    keyword = "right"
            self.d.press(keyword)
            self.d.sleep(0.2)

    def watch_tab(self, orientation="H"):
        """首页home持续切tab动作监听"""
        global keyword
        self.d.wait_activity(self.target_cls)
        print("run {}".format(time.time()))
        view = self.by_focused()
        if not view.exists:
            print("view is not exist")
            return
        try:
            center_point = view.center()
            print(center_point)
            if orientation == "H":
                if self.div(1470) <= center_point[0] <= self.div(1590) and self.div(107) <= center_point[1] <= self.div(
                        179):
                    keyword = "left"
                elif self.div(50) <= center_point[0] <= self.div(230) and self.div(107) <= center_point[1] <= self.div(
                        179):
                    keyword = "right"
        except Exception as e:
            raise e

    def init_view_state(self, view_name):
        self.d.press("home")
        self.d.sleep(1)
        view = self.by_xpath(view_name)
        if view is not None:
            view.wait().click()
        self.d.sleep(1)

    def delay_time_home_tab(self):
        """首页home切tab动作"""
        keycode = "right"
        print("start send key {}".format(time.time()))
        start_time_keycode = time.time()
        self.d.press(keycode)
        self.d.xpath(self.home_tab_switch_view).wait()
        print("end send key {}".format(time.time()))
        return round(time.time() - start_time_keycode, 2)

    def hot_boot_time_home(self, view_show_id):
        """首页home热启动打开动作"""
        self.d.app_start(self.target_pkg, wait=True, stop=True)
        view_show = self.d(text=view_show_id).wait(exists=True)
        if view_show:
            self.d.app_start("com.coocaa.os.softsettings", wait=True)
            '''随机操作10秒'''
            for x in range(10):
                self.d.press("down")
                self.d.sleep(1)
            print("start hot app {}".format(time.time()))
            time_start_activity = time.time()
            self.d.press("home")
            view_show = self.d(text=view_show_id).wait(exists=True)
            print(view_show)
            if view_show:
                print("end hot app {}".format(time.time()))
                activity_boot_time = time.time() - time_start_activity
                return round(activity_boot_time, 2)
        return -1

    def cold_boot_time_home(self, view_show_id):
        """首页home冷启动打开动作"""
        print("start app {}".format(time.time()))
        time_start_activity = time.time()
        self.d.app_start(self.target_pkg, wait=True, stop=True)
        self.d.wait_activity(self.target_cls)
        view_show = self.d(text=view_show_id).wait(exists=True)
        print(view_show)
        if view_show:
            print("end app {}".format(time.time()))
            activity_boot_time = time.time() - time_start_activity
            return round(activity_boot_time, 2)
        return -1

    def cold_boot_time_home_view_click_reset(self, view_click_tab_id=None, ):
        """首页界面入口View点击打开动作前重置操作"""
        self.d.app_start(self.target_pkg, wait=True, stop=True)
        if view_click_tab_id is not None:
            view = self.d.xpath(view_click_tab_id).wait()
            if view is not None:
                view.click()
            else:
                view = self.d(text=view_click_tab_id)
                view_show = view.wait(exists=True)
                if view_show:
                    view.click()

    def cold_boot_time_home_view_click(self, view_click_id, view_show_id):
        """首页界面入口View点击打开动作"""
        # self.d.app_start(self.target_pkg, wait=True, stop=True)
        # if view_click_tab_id is not None:
        #     self.d.xpath(view_click_tab_id).wait().click()
        view_click = self.d.xpath(view_click_id).wait(timeout=10)
        if view_click is not None:
            view_click.click()
            print("start app {}".format(time.time()))
            time_start_activity = time.time()
            view_show = self.d(text=view_show_id).wait(exists=True)  # self.d.xpath(view_show_id).wait()
            print(view_show)
            if view_show is not None:
                print("end app {}".format(time.time()))
                activity_boot_time = time.time() - time_start_activity
                return round(activity_boot_time, 2)
        return -1

    def boot_time_quick_panel_show(self, is_play_scene=True, boot_type="hot"):
        """
        首页便捷面版菜单键打开动作
        is_play_scene:是否是播放场景，默认是
        boot_type:启动类型，默认热启动
        """
        if boot_type != "hot":
            self.d.app_clear("com.coocaa.os.ccosservice")
            self.d.sleep(1)
        self.d.press("home")
        self.d.sleep(1)
        if not is_play_scene:
            self.d.xpath(self.init_start_view_tab).wait().click()
        self.d.xpath('//android.support.v7.widget.RecyclerView').wait()

        print("send menu keycode {}".format(time.time()))
        time_start_activity = time.time()
        self.d.press("menu")
        view_show = self.d.xpath(self.home_quick_panel_show_view).wait()
        print(view_show)
        if view_show is not None:
            print("end quick panel show {}".format(time.time()))
            activity_boot_time = time.time() - time_start_activity
            return round(activity_boot_time, 2)
        return -1

    def cold_boot_time_soft_settings_reset(self):
        """冷启动系统设置重置"""
        self.d.app_clear("com.coocaa.os.softsettings")
        self.d.sleep(2)
        print("start app {}".format(time.time()))

    def cold_boot_time_soft_settings(self):
        # """冷启动系统设置"""
        # self.d.app_clear("com.coocaa.os.softsettings")
        # self.d.sleep(2)
        # print("start app {}".format(time.time()))
        time_start_activity = time.time()
        self.d.app_start("com.coocaa.os.softsettings", wait=True)  # 启动应用
        # utils.shell("am start -n com.coocaa.simple.launcher/.NewActivity --es pkg com.coocaa.os.softsettings")
        # # self.d.wait_activity()
        # utils.shell(
        #     "sendevent /dev/input/event0 1 28 1 ;sendevent /dev/input/event0 0 0 0 ;sendevent /dev/input/event0 1 "
        #     "28 0 ;sendevent /dev/input/event0 0 0 0").wait()
        view_show = self.d(text="常规").wait(exists=True)  # 应用界面显示
        print("view_show:{}".format(view_show))
        if view_show:
            print("end app {}".format(time.time()))
            activity_boot_time = time.time() - time_start_activity
            return round(activity_boot_time, 2)
        return -1
