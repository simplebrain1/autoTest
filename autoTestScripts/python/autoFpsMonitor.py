import os
import shutil
import time
from glob import glob

import uiautomator2 as u2
import adbutils
# import shutil
# import json
import threading
# from threading import Lock, Thread
# from autoTestScripts.python.scriptUtils.image_match_utils import ImageMatch
from scriptUtils import utils, file_uitls, screenrecord

PATH = lambda p: os.path.abspath(p)

d = u2.connect()
deviceInfo = d.info
mDiv = 1.0  # 适配

print("-------------")
print(deviceInfo)
keyword = "down"  # "right"
fpsTimeout = 200  # 测试多长时间（按秒为单位）
saveFileName = "homeTab"
currentPkg = utils.get_current_package_name()
currentCls = utils.get_current_activity()
print("currentPkg:" + currentPkg + ",currentCls:" + currentCls)

# 测试的开始时间
startSwitchTabTime = time.time()  # datetime.datetime.now().strftime("%f")
deadline = time.time() + fpsTimeout
txt = " startSwitchTabTime:{}, deadline {}"
print(txt.format(startSwitchTabTime, deadline))


# 系统的版本号
# version = d._adb_shell("getprop ro.build.version.sdk")# print(d.info["sdkInt"])
# print(version)

# 初始化切tab
def initHomeTab():
    initStartApp()
    # d.xpath(
    #     '//*[@resource-id="android:id/content"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]').click()
    d.xpath("AI互动").click()


# 控件尺寸适配
def Div(x):
    mbaseScreenWith = 1920
    displayWidth = deviceInfo["displayWidth"]
    global mDiv
    mDiv = displayWidth / mbaseScreenWith
    # print("mDiv is {}".format(mDiv))

    if x < 0:
        return float(x * mDiv - 0.5)
    else:
        return float(x * mDiv + 0.5)


# 回到首页
def initStartApp():
    d.press("home")
    d.sleep(2)


# 修改切tab的按键
def setkeycode(key):
    global keyword
    keyword = key
    print("keyword:" + keyword)


def run(total):
    results = utils.shell(
        "sh /data/local/tmp/fps_info.sh {0} {1} {2}".format(total, "/data/local/tmp/" + saveFileName, currentPkg))
    print(results)


# 启动我的应用
def startStoreApp():
    print("start store app!")
    d.xpath(
        '//android.support.v7.widget.RecyclerView/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[3]').click()
    startTime = time.time_ns()  # datetime.datetime.now()#strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
    print(startTime)
    d.app_wait("com.tianci.appstore", front=True)
    endTime = time.time_ns()
    print(endTime)
    print("end store app!")


def startStoreAppWithCold():
    sess = d.session("com.tianci.appstore")  # start 我的应用
    # sess.close()  # 停止网易云音乐
    # sess.restart()  # 冷启动网易云音乐


# 开始全局监测提示框
def startMonitorGlobalWindow():
    # d.watcher.reset()
    d.watcher.when("好的").press("back")  # 弹出语音提示框的时候关闭
    d.watcher.when("关闭").click()
    d.watcher.when("稍后再说").click()
    d.watcher.when("取消").click()
    d.watcher.when("返回").click()
    d.watcher("ANR").when(xpath="ANR").click()
    d.watcher.start()


def stopMonitorGlobalWindow():
    d.watcher.stop()
    d.watcher.remove()


# 主页切tab动作(定位切换，控件定位会有耗时)
def switchHomeTab():
    i = 1
    global keyword

    while time.time() < deadline:
        d.press(keyword)
        d.sleep(0.2)
        print(i)
        if i % 18 == 0:
            if keyword == "left":
                keyword = "right"
            elif keyword == "right":
                keyword = "left"
        i = i + 1

    print("fps monitor completion")


# 控件定位
def switchHomeTab2():
    i = 1
    global keyword
    while time.time() < deadline:
        center_point = d(focused="true").center()
        print(center_point)
        if Div(1606) <= center_point[0] <= Div(1830) and Div(107) <= center_point[1] <= Div(179):
            keyword = "left"
        elif Div(50) <= center_point[0] <= Div(230) and Div(107) <= center_point[1] <= Div(179):
            keyword = "right"
        d.press(keyword)
        print(i)
        i = i + 1

    print("fps monitor completion")


def mvDeviceToWin():
    path = PATH("{}/FpsFiles/".format(os.getcwd()))
    if not os.path.isdir(path):
        os.makedirs(path)
    utils.adb("pull /data/local/tmp/" + saveFileName + " " + path)
    # os.removedirs("FpsFiles")
    # shutil.rmtree("FpsFiles")


def pushFpsUtilsToDevice():
    path = PATH("{}/shell/fps_info.sh".format(os.getcwd()))
    if not os.path.exists(path):
        print("fps_info.sh is no find")
        return
    utils.adb(
        "push " + path + " /data/local/tmp").wait()
    d.push(path, "/data/local/tmp/")
    print("push fps_info.sh succeed.")


# 模拟主页tab切换
def monitorHomeTab():
    # pushFpsUtilsToDevice()
    # # 开启一个线程去执行sh脚本
    # t = threading.Thread(target=run, args=(fpsTimeout,))
    # t.start()
    # startMonitorGlobalWindow()  # 开启监控

    # 模拟homeTab人工操作
    initHomeTab()
    switchHomeTab2()

    # stopMonitorGlobalWindow()  # 停止监控

    # mvDeviceToWin()  # 自动把抓到的数据移到项目fpsFiles下

    print("monitor is end")


# 模拟主页切内容
def monitorHomeContent():
    # pushFpsUtilsToDevice()
    # d.xpath(
    #     '//*[@resource-id="android:id/content"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[6]').click()
    d.xpath("影视").click()
    i = 1
    global keyword
    keyword = "down"
    while time.time() < deadline:
        center_point = d(focused="true").center()
        # bounds = d(focused="true").bounds()
        # print(bounds)
        print(center_point)

        if Div(80) <= center_point[0] <= Div(348) and Div(600) <= center_point[1] <= Div(974):
            keyword = "up"
        elif Div(857) <= center_point[0] <= Div(1001) and Div(107) <= center_point[1] <= Div(179):
            keyword = "down"
        # if d(focused="true").down(className="android.widget.FrameLayout").exists:
        #     keyword = "up"
        d.press(keyword)


#
# def _async_raise(tid, exctype):
#     """raises the exception, performs cleanup if needed"""
#     tid = ctypes.c_long(tid)
#     if not inspect.isclass(exctype):
#         exctype = type(exctype)
#     res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
#     if res == 0:
#         raise ValueError("invalid thread id")
#     elif res != 1:
#         # """if it returns a number greater than one, you're in trouble,
#         # and you should call it again with exc=NULL to revert the effect"""
#         ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
#         raise SystemError("PyThreadState_SetAsyncExc failed")
#
# def stop_thread(thread):
#     _async_raise(thread.ident, SystemExit)

# def record():
#     dd = adbutils.adb.device()
#     current_time = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))
#     screenrecord_file_name = 'log_screenrecord_' + current_time + '.mp4'
#     folder_path = 'D:\\ALOG\\'
#     screenrecord_file_path = os.path.join(folder_path, 'screenrecord', screenrecord_file_name)
#     sc = dd.screenrecord("/sdcard/s.mp4")
#     time.sleep(15)  # 录制15s视频
#     sc.stop_and_pull(screenrecord_file_path)


def wait_activity(activity, timeout=10):
    """ wait activity
    Args:
        activity (str): name of activity
        timeout (float): max wait time

    Returns:
        bool of activity
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        current_activity = utils.get_current_activity()
        if activity == current_activity:
            return True
        time.sleep(.5)
    return False


def get_keyword(keycode):
    print("keycode {}".format(keycode))
    return keycode


if __name__ == "__main__":
    # if not input("Make sure the test Activity, in this process, you should keep in this Activity!\n"
    #              "Please press Enter continue..."):
    #     dump_time = -1
    #     while dump_time < 120:
    #         try:
    #             txt = input("Please input dump times: ")
    #             dump_time = int(txt)
    #             if dump_time < 120:
    #                 print("Min dumptimes is 120,please input dumptimes>120!")
    #         except:
    #             print("dump times is invaild!")
    #             continue
    #
    # fpsTimeout = dump_time
    # print(dump_time)
    # d.wait_activity()
    # print(d.image.match("look.png"))
    # print(os.getcwd())
    # monitorHomeTab()
    # monitorHomeContent()
    # view = d.xpath('//*[@text="AI互动"]')
    # view.
    # view.set_text("111")
    # view.
    # view_info = d(focused="true").wait()
    # print(view_info.info)
    # d.screen_on()
    # d.screen_off()
    # view = d.xpath("看电视").wait().click()
    # print(view.bounds)
    # print(view.center())
    # u2.current
    # print(view_info["childCount"])
    # print(d.window_size())
    # print(d.screenshot)
    # print(d.info["sdkInt"])
    # path = PATH("{}/Img/".format(os.getcwd()))
    # if not os.path.isdir(path):
    #     os.makedirs(path)
    # print("screenshot start {}".format(time.time()))
    # x = d.xpath("VIP").screenshot()
    # print("screenshot start1 {}".format(time.time()))
    # print(x.save(path+"/vip.png"))
    # path = PATH("{}/Img/".format(os.getcwd()))
    # if not os.path.isdir(path):
    #     os.makedirs(path)
    # d.screenrecord('./test2.mp4')  # 开始
    # # screenrecord.record_start(4)
    # time.sleep(2)
    # d.press("home")
    # time.sleep(2)
    # d.xpath("我的应用").click()
    # time.sleep(5)
    # 启动录制，默认帧率为 20
    # d.screenrecord('test.mp4')
    # print(d.app_current())

    # 其它操作
    # time.sleep(4)
    # 停止录制，只有停止录制了才能看到视频
    # x = d.screenrecord.stop()
    # print(x)
    # file_uitls.move_fpsdata_to_save(d,"minicap-images")
    # print("screenrecord end")
    # d.toast.show("Helloworld")
    # print(d.image.match("look.png"))

    # d.open_url("https://www.baidu.com")

    # print(time.time())

    # x =  d.implicitly_wait()#d.wait_timeout
    # print(x)
    # d.wait_activity()

    # initStartApp()
    # startStoreApp()
    # startStoreAppWithCold()

    # sess = d.session("com.coocaa.os.softsettings",attach=True)
    # sess.close()  # 停止网易云音乐
    # sess.restart()

    # print(d.app_current())
    # d.app_stop("com.coocaa.os.softsettings")
    # print("start app {}".format(time.time()))
    # d.app_start("com.coocaa.os.softsettings", ".framework.ui.SettingsActivity")
    # show = d.wait_activity(".framework.ui.SettingsActivity")
    # print(show)
    # if show:
    #     print("end app {}".format(time.time()))

    # d.app_stop("com.tianci.movieplatform")
    # d.press("home")
    # d.app_start("com.tianci.movieplatform",wait=True,stop=True)
    # d.sleep(1)
    # d.press("home")
    # d.sleep(1)
    # d.xpath('//*[@resource-id="android:id/content"]/android.widget.FrameLayout[1]/android.widget.FrameLayout['
    #         '4]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.view.View[1]').wait().click()
    # print("start app {}".format(time.time()))
    # d.app_start("com.tianci.movieplatform", ".SkySearchActivity")
    # show = wait_activity(".SkySearchActivity")
    # viewshow = d(text="热搜推荐").wait(exists=True)
    # print(viewshow)
    # if viewshow:
    #     print("end app {}".format(time.time()))
    # print(show)
    # if show:
    #     print("end app {}".format(time.time()))
    # print("--{}  --{}".format(d.app_current(),utils.get_current_activity()))
    # print("start find view {}".format(time.time()))
    # if d(text="我的应用").wait(exists=True):
    # if d(focused="true").wait(exists=True):
    # if d(text="影视").exists:
    # if d.xpath("AI互动").exists:
    # d.xpath('//android.support.v7.widget.RecyclerView/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[3]').click()
    #     print("find view {}".format(time.time()))
    #     d(text="影视").click()

    # d.xpath("VIP").screenshot("vip.png")
    # d.screenshot("vip_home.png")
    # # 图像匹配test
    # im = ImageMatch()
    # print("start match {}".format(time.time()))
    # img = "vip_home.png"
    # print(im.match_img(img))
    # print("end match {}".format(time.time()))
    # keyword = "right"
    # d.watcher.when().call()
    # d.watcher("ANR").when(xpath="ANR").click()
    # d.watcher.start()
    # if not d(focused="true").b.exists:
    #     pass
    # print(time.time())
    # print(d(focused="true").left(className="android.widget.FrameLayout"))
    # if view is not None:
    #     d.press("right")
    # print(view)
    # d.xpath('//android.support.v7.widget.RecyclerView/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]').wait()
    # d.xpath(
    #     '//*[@resource-id="android:id/content"]/android.widget.FrameLayout[1]/android.widget.FrameLayout['
    #     '2]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]').wait()
    # d.xpath(
    #     '//android.support.v7.widget.RecyclerView/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]').wait()
    # d.xpath('//*[@resource-id="android:id/content"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[7]/android.widget.LinearLayout[1]').wait()
    # print(d(text="少儿").get_text())
    # print(time.time())
    # d.screen_off()
    # exit_code = d.shell("pwd").exit_code
    # print(exit_code)
    # print(d.xpath(
    # '//*[@resource-id="android:id/content"]/android.widget.FrameLayout[1]/android.widget.FrameLayout['
    # '1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout['
    # '1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]').match().info.)
    # srcfile = "./shell/fps_info_parse.sh"
    # dstpath = "./FpsFiles/"
    # if not os.path.isfile(srcfile):
    #     print("%s not exist!" % (srcfile))
    # else:
    #     fpath, fname = os.path.split(srcfile)  # 分离文件名和路径
    #     # if not os.path.exists(dstpath):
    #     #     os.makedirs(dstpath)  # 创建路径
    #     # src_file_list = glob("./FpsFiles/" + '*')  # glob获得路径下所有文件，可根据需要修改
    #     # for srcfile in src_file_list:
    #     #     print(srcfile)
    #     # for file_abs in glob.("./FpsFiles/"):
    #     #     print(file_abs)
    #     for root, dirs, files in os.walk(dstpath):
    #         # print(root)
    #         # print(dirs)
    #         # print(files)
    #         if len(files) > 0 and fname not in files:
    #             shutil.copy(srcfile, root + "\\" + fname)
    # assert
    # print(utils.get_app_pid("com.tianci.movieplatform"))
    # print(d.app_current().get("pid"))
    # print(utils.get_app_pid("com.tianci.movieplatform"))

    # d.shell("pm clear com.coocaa.os.ccossservice")
    # utils.shell("pm clear com.coocaa.os.ccosservice")
    # shutil.copy(srcfile, dstpath + fname)  # 复制文件
    # print("copy %s -> %s" % (srcfile, dstpath + fname))

    print("start {}".format(time.time()))
    start = time.time()

    # print(utils.get_current_activity())
    # print(d(focused="true").child(className="android.widget.TextView").get_text())
    # utils.("input  22")
    # command = os.path.join(f"D:\\studioSDK\\ffmpeg-5.0.1-essentials_build\\bin", "ffmpeg.exe")
    # if not os.path.exists(command):
    # command = os.path.join("ffmpeg.exe")
    # is_show = d(text="QQ音乐").wait(exists=True,timeout=10)
    # print("is_show:{}".format(is_show))
    # utils.shell("sendevent /dev/input/event0 1 28 1 ;sendevent /dev/input/event0 0 0 0 ;sendevent /dev/input/event0 1 "
    #             "28 0 ;sendevent /dev/input/event0 0 0 0").wait()
    # print(utils.shell("getprop ro.product.model").stdout.read().decode())
    # print(d.device_info)
    d.touch.down(161, 85)
    time.sleep(1)
    d.touch.up(161, 85)
    # time.sleep(2)
    # utils.shell("sendevent /dev/input/event0 1 115 0 ;sendevent /dev/input/event0 0 0 0").wait()
    # utils.shell("")
    # print(d.shell("getprop ro.product.model").output)
    print("end {}".format(time.time() - start))
    # d.wait_activity()
    # # d.xpath("").wait()
    # d(text="电影").chget_text().wait(exists=True)
