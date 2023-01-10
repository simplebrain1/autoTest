#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import uiautomator2 as u2

from autoTestScripts.python.pages.home_page import HomePage
from autoTestScripts.python.scriptUtils import file_uitls, utils
from autoTestScripts.python.base_test import BaseTestCase

"""系统设置UI层级获取TestCase"""
PATH = lambda p: os.path.abspath(p)


class TestSoftSettingUiHierarchy(BaseTestCase):
    def setup(self):
        self.tag_cn = '设置UI层级'
        self.tag = 'TestSoftSettingUiHierarchy'
        print("you are testing apk is :" + self.current_pkg + " ,apk_cls:" + self.current_cls + ",tag:" + self.tag)
        self.save_file_name = self.tag
        self.home = HomePage(self.d)
        self.enable_record = False
        self.enable_auto_analyse = False
        self.target_boot_pkg = "com.coocaa.os.softsettings"
        self.target_show_view = "常规"

        self.stagesepx_with_keras_dir = "../../stagesepx_with_keras"

    def test_case_reset(self):
        self.home.cold_boot_time_app_reset(self.target_boot_pkg)

    def test_action(self):
        # 酷开系统开放平台 https://beta-webapp.skysrt.com/doc/coocaa/os/swaiot-api/zh/app/development/docs/%E7%B3%BB%E7%BB%9F%E6%9C%8D%E5%8A%A1/%E8%AE%BE%E7%BD%AE%E6%A1%86%E6%9E%B6.html#%E4%B9%9D%E3%80%81%E9%A1%B5%E9%9D%A2%E8%B7%B3%E8%BD%AC
        test_dict = {
                     '设置': "coocaa.intent.action.SETTINGS",
                     '通用': "android.settings.GENERAL_SYSTEM_SETTINGS",
                     '应用管理': "coocaa.intent.action.APP_MANAGER",
                     '通知管理': "coocaa.intent.action.NOTIFICATION_MANAGER",
                     '个性化': "coocaa.intent.action.PERSONALIZATION",
                     '智能个性化': "coocaa.intent.action.SMART_PERSONALIZATION",
                     '模式': "coocaa.intent.action.MODE",
                     '用户参与改进计划-含开关': "coocaa.intent.action.USER_IMPROVE_PLAN",
                     '用户参与改进计划-纯说明': "coocaa.intent.action.USER_IMPROVE",
                     '对话制作团队': "com.coocaa.os.action.PRESENT_TEAM",
                     '关于本机': "	coocaa.intent.action.ABOUT_TV",
                     '系统更新': "android.settings.SYSTEM_UPGRADE",

                     '本机名称': "android.settings.DEVICE_NAME",
                     '本机信息': "android.settings.EQUIP_INFO",
                     '存储空间': "coocaaa.intent.action.setting.STORAGE",
                     '保修信息': "coocaa.intent.action.WARRANTY",
                     '联系客服': "coocaa.intent.action.CUSTOMER_SERVICE",
                     '法律与监管': "coocaa.intent.action.LEGAL_SUPERVISION",
                     '认证标识': "coocaa.intent.action.CERTIFICATION_MARK",

                     '服务协议': "coocaa.intent.action.WEB_SERVICE",  # 隐私政策,开放源代码许可,预置应用同页面

                     '应用开源声明	': "coocaa.intent.action.OPEN_APP",
                     '地理位置': "com.coocaa.os.softsettings.LOCATION_MANAGER	",
                     '不常用应用': "com.coocaa.os.softsettings.LESS_USED_APP_MANAGER",
                     '流畅度选项(旧)': "com.coocaa.os.softsettings.APP_ENABLE_MANAGER",
                     '流畅度选项': "	coocaa.intent.action.FLUENCY",
                     }
        print(self.tag + " is start")
        # 设置主界面
        #duration = self.home.cold_boot_time_app(self.target_show_view)
        #print("start target Activity time {}".format(duration))
        # 很多页面是复用activity的，看是否可以用action代替
        for key, value in test_dict.items():
            if key == '服务协议':
                self.home.open_target_app_page_by_action(value, key, extra_key="modualName",
                                                         extra_string_value="service_contract")
            else:
                self.home.open_target_app_page_by_action(value, key)
            # 页面稳定再获取
            self.d.sleep(5)
            hierarchy = utils.get_view_tree_hierarchy(self.d)
            print("%s 页面UI层级:%d" % (key, hierarchy))
            file_uitls.save_app_perf_data(self.save_file_name,
                                          app_info=self.d.app_info(self.target_boot_pkg),
                                          standard_value=10,
                                          test_type="UI层级",
                                          test_subcategories=str(key),
                                          test_content=str(key),
                                          test_result=str(hierarchy),
                                          )
        self.test_completion.set()
        print(self.tag + " is end")


if __name__ == "__main__":
    d = u2.connect(utils.get_serial_num())
    test = TestSoftSettingUiHierarchy(d)  # 创建测试对象
    test.setup()  # 初始化
    test.test_case()  # 开始测试
