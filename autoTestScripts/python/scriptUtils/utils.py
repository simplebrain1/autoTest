#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import platform
import re
import subprocess
import time
import tkinter as tk
from tkinter import ttk
from typing import Union

from uiautomator2 import Device
import xml.etree.ElementTree as ET

from autoTestScripts.python.scriptUtils import exception

serial_num = ""

# 判断系统类型，windows使用findstr，linux使用grep
system = platform.system()
if system == "Windows":
    find_util = "findstr"
else:
    find_util = "grep"
print(find_util)
# 判断是否设置环境变量ANDROID_HOME
command = ""
if "ANDROID_HOME" in os.environ:
    if system == "Windows":
        command = os.path.join(os.environ["ANDROID_HOME"], "platform-tools", "adb.exe")
    else:
        command = os.path.join(os.environ["ANDROID_HOME"], "platform-tools", "adb")
else:
    if system == "Windows":
        user_name = os.environ['USERNAME']
        command = os.path.join(f"C:\\Users\\{user_name}\\AppData\\Local\\Android\\Sdk", "platform-tools", "adb.exe")
if os.path.exists(command):
    pass
else:
    raise EnvironmentError(
        "Adb not found in $ANDROID_HOME path: %s." % os.environ["ANDROID_HOME"])


def get_screen_size(window):
    return window.winfo_screenwidth(), window.winfo_screenheight()


def get_window_size(window):
    return window.winfo_reqwidth(), window.winfo_reqheight()


def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    root.geometry(size)


class Window(object):
    device_id = ""
    device_id_list = []
    device_name_list = []
    device_name_dict = {}
    root = None
    box = None

    def __init__(self, device_id_list, root):
        self.device_id_list = device_id_list
        self.device_name_dict = get_device_name_dict(self.device_id_list)
        self.get_device_name_list()
        self.device_id = device_id_list[0]
        self.root = root
        self.box = None

    def show_window(self):
        self.root.title(u'Serialno Number')
        center_window(self.root, 300, 240)
        self.root.maxsize(600, 400)
        self.root.minsize(300, 240)

        # options = self.device_id_list
        options = self.device_name_list
        self.box = ttk.Combobox(values=options)
        self.box.current(0)
        self.box.pack(expand=tk.YES)
        self.box.bind("<<ComboboxSelected>>", self.select)
        ttk.Button(text=u"确定", command=self.ok).pack(expand=tk.YES)

        self.root.mainloop()

    def select(self, event=None):
        for key, value in self.device_name_dict.iteritems():
            if value == self.box.selection_get():
                self.device_id = key
        # self.device_id = self.box.selection_get()

    def ok(self):
        global serial_num
        serial_num = self.device_id
        self.root.destroy()

    def get_device_name_list(self):
        for id in self.device_id_list:
            self.device_name_list.append(self.device_name_dict.get(id))


def get_serial_num():
    global serial_num
    if serial_num == "":
        devices = get_device_list()
        if len(devices) == 1:
            serial_num = devices[0]
        else:
            root = tk.Tk()
            window = Window(devices, root)
            window.show_window()
    return serial_num


# adb命令
def adb(args):
    global serial_num
    if serial_num == "":
        devices = get_device_list()
        if len(devices) == 1:
            serial_num = devices[0]
        else:
            root = tk.Tk()
            window = Window(devices, root)
            window.show_window()
    cmd = "%s -s %s %s" % (command, serial_num, str(args))
    print(cmd)
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# adb shell命令
def shell(args):
    global serial_num
    if serial_num == "":
        devices = get_device_list()
        if len(devices) == 1:
            serial_num = devices[0]
        else:
            root = tk.Tk()
            window = Window(devices, root)
            window.show_window()
    # 给shell命令增加双引号，避免在Windows下面无法识别某些linux命令导致出错，uiautomator2自带adb工具无此问题
    cmd = '%s -s %s shell "%s"' % (command, serial_num, str(args))
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# 获取设备状态
def get_state():
    return os.popen("adb -s %s get-state" % serial_num).read().strip()


# 获取对应包名的pid
def get_app_pid(pkg_name):
    if system == "Windows":
        string = shell("ps | findstr %s$" % pkg_name).stdout.read()

    string = shell("ps -a| grep -w %s" % pkg_name).stdout.read().decode()

    print(string)
    if string == '':
        return "the process doesn't exist."

    pattern = re.compile(r"\d+")
    result = string.split(" ")
    result.remove(result[0])

    return pattern.findall(" ".join(result))[0]


# 杀掉对应包名的进程
def kill_process(pkg_name):
    pid = get_app_pid(pkg_name)

    result = shell("kill %s" % str(pid)).stdout.read().split(": ")[-1]

    if result != "":
        raise exception.ScriptException("Operation not permitted or No such process")


# 获取设备上当前应用的包名与activity
def get_focused_package_and_activity():
    pattern = re.compile(r"[a-zA-Z0-9\.]+/.[a-zA-Z0-9\.]+")
    # tmp = shell("dumpsys activity | %s mFocusedActivity" %find_util).stdout.read()
    tmp = shell("dumpsys activity | grep mResumedActivity").stdout.read()
    tmp = tmp.decode()
    print("get_focused_package_and_activity命令执行结果:{}".format(tmp))
    name = ""
    names = pattern.findall(tmp)
    print("get_focused_package_and_activity:{}".format(names))
    if names.__len__() == 0:
        return ""
    try:
        name = names[0]
    except:
        tmp = shell("dumpsys window w | grep / | grep name=").stdout.read()
        tmp = tmp.decode()
        name = pattern.findall(tmp)[0]
    return name


def get_input_device_path(device_default_name: str = "IR"):
    if device_default_name is None:
        device_default_name = "IR"
    device_path = ""
    for x in range(15):
        file = "/sys/class/input/event%d/device/name" % x
        result = shell('if [ -f "%s" ];then cat "%s"; else echo "no"; fi;' % (file, file)).stdout.read().decode()
        print("file %s,device_path:%s" % (file, result))
        m = re.search(device_default_name, result, re.IGNORECASE)
        if bool(m):
            device_path = "/dev/input/event%d" % x
            break

    print("device_path:%s" % device_path)
    return device_path


# 方便电视按键监测
def send_key_event(device_path: str, key: Union[int, str], long_press_flag: bool = False, press_time: float = 5):
    """
    press key via name or key code (linux not android). Supported key name includes:
    home, left, right, up, down, enter, select
    """
    key_dict = {'enter': 28, 'home': 102, 'up': 103, "left": 105, 'right': 106, 'down': 108, 'select': 353}
    if isinstance(key, int):
        key_code = key
    else:
        key_code = key_dict[key]
    print("send_key_event keycode: %d" % key_code)
    cmd_down = 'sendevent %s 1 %d 1' % (device_path, key_code)
    cmd2 = 'sendevent %s 0 0 0' % device_path
    cmd_up = 'sendevent %s 1 %d 0' % (device_path, key_code)
    if long_press_flag:
        deadline = time.time() + press_time
        shell(cmd_down + ' && ' + cmd2)
        while time.time() <= deadline:
            pass
        shell(cmd_up + ' && ' + cmd2)
    else:
        shell(cmd_down + ' && ' + cmd2 + " && " + cmd_up + " && " + cmd2)


# 获取当前应用的包名
def get_current_package_name():
    return get_focused_package_and_activity().split("/")[0]


# 获取当前设备的activity
def get_current_activity():
    return get_focused_package_and_activity().split("/")[-1]


hierarchy_flag = False
hierarchy_num = 0
max_hierarchy = 0


def walk_data(root_node):
    global hierarchy_flag, hierarchy_num, max_hierarchy
    print(root_node.tag, root_node.attrib)
    if root_node.tag == "node":
        if hierarchy_flag:
            hierarchy_num += 1
            max_hierarchy = max(max_hierarchy, hierarchy_num)
        if root_node.attrib['resource-id'] == 'android:id/content':
            hierarchy_flag = True

    children_node = root_node.findall('node')
    for child in children_node:
        walk_data(child)

    if root_node.tag == "node":
        if hierarchy_flag:
            hierarchy_num -= 1
        if root_node.attrib['resource-id'] == 'android:id/content':
            hierarchy_flag = False
    return


def get_view_tree_hierarchy(d: Device):
    global hierarchy_flag, hierarchy_num, max_hierarchy
    hierarchy_flag = False
    hierarchy_num = 0
    max_hierarchy = 0
    print('get_view_tree_hierarchy')
    xml = d.dump_hierarchy()
    root = ET.fromstring(xml)
    print('root_tag:', root.tag)
    print(xml)
    walk_data(root)
    print("view_max_hierarchy: %d" % max_hierarchy)
    return max_hierarchy


# 时间戳
def timestamp():
    return time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))


def get_device_list():
    devices = []
    result = subprocess.Popen("adb devices", shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).stdout.readlines()
    result.reverse()
    for line in result[1:]:
        line = line.decode()
        if "attached" not in line.strip():
            devices.append(line.split()[0])
        else:
            break
    return devices


def get_device_name_dict(devices):
    device_dict = {}
    if not devices:
        return

    for device in devices:
        cmd = "adb -s %s shell getprop ro.product.model" % device
        device_name = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE).stdout.readline().strip()
        device_dict[device] = device_name
    return device_dict


# 连接设备
# adb("kill-server").wait()
# adb("start-server").wait()
adb("wait-for-device").wait()

if get_state() != "device":
    adb("kill-server").wait()
    adb("start-server").wait()

if get_state() != "device":
    raise exception.ScriptException("Device not run")

if __name__ == "__main__":
    print(get_focused_package_and_activity())
