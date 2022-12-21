#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading

import uiautomator2 as u2

from autoTestScripts.python.pages.educate_home_page import EducateHomePage
from base_test import BaseTestCase
from scriptUtils import file_uitls

"""
儿童教育主页切Tab帧信息TestCase
执行完脚本，自动操作并在目前下/FpsFiles/educateHomeTab/下生成对应的帧数据文件fps_temp.txt
"""


class TestEducateHomeTabSwitch(BaseTestCase):
    def setup(self):
        self.tag = "儿童教育主页切Tab帧信息测试"
        print("you are testing apk is :" + self.current_pkg + " ,apk_cls:" + self.current_cls + ",tag:" + self.tag)
        self.save_file_name = "educateHomeTab"
        self.enable_record = False
        self.home = EducateHomePage(self.d)
        self.timeout = 180  # 测试的时间，单位为秒
        print("  timeout {}".format(self.timeout))

    def run(self, total):
        if self.version > 23:
            cmd = "sh /data/local/tmp/fps_info.sh {0} {1} {2}".format(total, "/data/local/tmp/" + self.save_file_name,
                                                                      self.home.target_pkg)
        else:
            cmd = "sh /data/local/tmp/fps_info.sh {0} {1} {2} {3}".format(total,
                                                                          "/data/local/tmp/" + self.save_file_name,
                                                                          self.home.target_pkg + "/" + self.home.target_cls + "#0",
                                                                          "1")
        # utils.shell(cmd).wait()
        self.d.shell(cmd, timeout=total)
        print("run test end {}".format(cmd))
        self.test_completion.set()

    def test_action(self):
        print("testHomeTabSwitch is start")
        has_tool = file_uitls.push_fpstool_to_device(self)
        if not has_tool:
            return
        try:
            t = threading.Thread(target=self.run, args=(self.timeout,))
            t.start()
            self.home.watcher.start(target=self.home.watch_tab, args=("H",))
            self.home.monitor_home_tab(self.timeout)
            self.home.watcher.stop()
            self.d.sleep(1)
            file_uitls.move_fps_data_to_save(self, self.save_file_name)
            self.d.sleep(1)
            print("TestEducateHomeTabSwitch is end")
        except Exception as e:
            self.home.watcher.stop()
            self.test_completion.set()
            self._end_test()
            print("TestEducateHomeTabSwitch is exception!".format(e))
            raise e


if __name__ == "__main__":
    d = u2.connect()
    test = TestEducateHomeTabSwitch(d)  # 创建测试对象
    test.setup()  # 初始化
    test.test_case()  # 开始测试
