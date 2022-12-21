#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import time

from uiautomator2 import Device

DEFAULT_SECONDS = 10


class BasePage(object):
    def __init__(self, device: Device):
        self.d = device
        self.watcher = WatcherView()

    def by_id(self, id_name):
        """通过id定位单个元素"""
        try:
            self.d.implicitly_wait(DEFAULT_SECONDS)
            return self.d(resourceId=id_name)
        except Exception as e:
            print("页面中没有找到id为%s的元素" % id_name)
            raise e

    def by_id_matches(self, id_name):
        """通过id关键字匹配定位单个元素"""
        try:
            self.d.implicitly_wait(DEFAULT_SECONDS)
            return self.d(resourceIdMatches=id_name)
        except Exception as e:
            print("页面中没有找到id为%s的元素" % id_name)
            raise e

    def by_class(self, class_name):
        """通过class定位单个元素"""
        try:
            self.d.implicitly_wait(DEFAULT_SECONDS)
            return self.d(className=class_name)
        except Exception as e:
            print("页面中没有找到class为%s的元素" % class_name)
            raise e

    def by_text(self, text_name):
        """通过text定位单个元素"""
        try:
            self.d.implicitly_wait(DEFAULT_SECONDS)
            return self.d(text=text_name)
        except Exception as e:
            print("页面中没有找到text为%s的元素" % text_name)
            raise e

    def by_class_text(self, class_name, text_name):
        """通过text和class多重定位某个元素"""
        try:
            self.d.implicitly_wait(DEFAULT_SECONDS)
            return self.d(className=class_name, text=text_name)
        except Exception as e:
            print("页面中没有找到class为%s、text为%s的元素" % (class_name, text_name))
            raise e

    def by_text_match(self, text_match):
        """通过textMatches关键字匹配定位单个元素"""
        try:
            self.d.implicitly_wait(DEFAULT_SECONDS)
            return self.d(textMatches=text_match)
        except Exception as e:
            print("页面中没有找到text为%s的元素" % text_match)
            raise e

    def by_desc(self, desc_name):
        """通过description定位单个元素"""
        try:
            self.d.implicitly_wait(DEFAULT_SECONDS)
            return self.d(description=desc_name)
        except Exception as e:
            print("页面中没有找到desc为%s的元素" % desc_name)
            raise e

    def by_xpath(self, xpath):
        """通过xpath定位单个元素【特别注意：只能用d.xpath，千万不能用d(xpath)】"""
        try:
            self.d.implicitly_wait(DEFAULT_SECONDS)
            return self.d.xpath(xpath)
        except Exception as e:
            print("页面中没有找到xpath为%s的元素" % xpath)
            raise e

    def by_id_text(self, id_name, text_name):
        """通过id和text多重定位"""
        try:
            self.d.implicitly_wait(DEFAULT_SECONDS)
            return self.d(resourceId=id_name, text=text_name)
        except Exception as e:
            print("页面中没有找到resourceId、text为%s、%s的元素" % (id_name, text_name))
            raise e

    def find_child_by_id_class(self, id_name, class_name):
        """通过id和class定位一组元素，并查找子元素"""
        try:
            self.d.implicitly_wait(DEFAULT_SECONDS)
            return self.d(resourceId=id_name).child(className=class_name)
        except Exception as e:
            print("页面中没有找到resourceId为%s、className为%s的元素" % (id_name, class_name))
            raise e

    def is_text_loc(self, text):
        """定位某个文本对象（多用于判断某个文本是否存在）"""
        return self.by_text(text_name=text)

    def is_id_loc(self, id):
        """定位某个id对象（多用于判断某个id是否存在）"""
        return self.by_id(id_name=id)

    def by_focused(self):
        """定位获取焦点的对象"""
        try:
            self.d.implicitly_wait(DEFAULT_SECONDS)
            return self.d(focused="true")
        except Exception as e:
            print("页面中没有focused=true的元素")
            raise e

    def div(self, x):
        """控件尺寸适配"""
        base_screen_width = 1920
        display_width = self.d.info["displayWidth"]
        div = display_width / base_screen_width
        if x < 0:
            return float(x * div - 0.5)
        else:
            return float(x * div + 0.5)


'''
view观察类
'''


class WatcherView:
    def __init__(self):
        self._target = None
        self._args = None
        self._watch_stopped = threading.Event()
        self._watching = False  # func start is calling

    def start(self, interval: float = 2.0, target=None, args=()):
        """ start watcher """
        if self._watching:
            print("already started")
            return
        self._target = target
        self._args = args
        self._watching = True
        th = threading.Thread(name="watcher_view",
                              target=self.watch_immediately,
                              args=(interval,))
        th.start()
        return th

    def stop(self):
        """ stop watcher """
        print("stop watcher")
        if not self._watching:
            print("watch already stopped")
            return

        if self._watch_stopped.is_set():
            return

        self._watch_stopped.set()
        ret = self._watch_stopped.wait(10.0)
        # print(self._watch_stopped.is_set())
        print("stop watcher--0".format(ret))
        # # reset all status
        # self._watching = False
        # self._watch_stopped.clear()
        print("stop watcher--1")
        return ret

    def watch_immediately(self, interval: float):
        try:
            time.sleep(interval)
            while not self._watch_stopped.wait(timeout=interval):
                print(self._watch_stopped.is_set())
                self.run()
        finally:
            print("watcher_immediately end")
            # reset all status
            self._watching = False
            self._watch_stopped.clear()

    def run(self):
        try:
            if self._target is not None:
                self._target(*self._args)
        finally:
            pass
