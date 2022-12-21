import os
import threading
import time

from stagesepx.classifier import ClassifierResult
from uiautomator2 import Device

from autoTestScripts.python.scriptUtils import screenrecord, stagesepx_utils
from autoTestScripts.python.scriptUtils import utils

PATH = lambda p: os.path.abspath(p)


class BaseTestCase:
    def __init__(self, device: Device):
        self.d = device
        self.d.settings['wait_timeout'] = 10.0  # 默认控件等待时间
        self.timeout = 60  # 帧率采取时间，默认180秒
        self.tag = "default_tag"
        self.test_completion = threading.Event()  # 单个自动化测试运行是否结束的标识变量
        self.enable_record = True  # 是否需要录制开关，默认关
        self.time_before_record = 2  # 发生动作前视频录制前置多长时间，单位秒
        self.time_after_stop_record = 0  # 发生动作结束后视频录制后置多长时间，单位秒
        self.enable_auto_analyse = False  # 是否视频自动分析开关，需提前对待测视频建立预测模型
        self.camera_type = "local" # "outlay"  # 摄像头类型，local：使用的设备的screenrecord,outlay：外置摄像头，需下载ivCam或附带摄像头
        if "outlay" == self.camera_type:
            self.time_after_stop_record = 5  # 外置摄像头时，防止动作结束录制实时结束导致可能出现未录全情况，置后5秒停止录制
        self.record_timeout = 20  # camera_type为local时录制时间，默认为20秒，camera_type为”outlay“时，视频根据api调用实时结束
        self.save_result_dir = "resultDatas"  # 自动化示例计算时间结果存放目录名称，不配置，默认为resultDatas
        self.stagesepx_frame_blocking_dir = "picture"  # 视频预测模型.h5文件及视频稳定帧分区帧图片存入目录名称
        self.stagesepx_result_dir = "stagesepxResultDatas"  # 自动化示例视频模型解析存放结果目录名称
        self.save_file_name = "default"  # 单个自动化脚本结果保存文件夹名称，未配置则为”default“
        self.sum_save_file_name = "AllResult"  # 批量执行自动化脚本结果汇总保存文件名称，未配置则为”AllResult“
        self.current_pkg = utils.get_current_package_name()
        self.current_cls = utils.get_current_activity()
        self.version = device.info["sdkInt"]  # 设备sdk版本

    def setup(self):
        pass

    def start_monitor_global_window(self):
        """开始全局监测提示框"""
        # d.watcher.reset()
        try:
            self.d.watcher.when("好的").press("back")  # 弹出语音提示框的时候关闭
            self.d.watcher.when(" 按【返回键】可关闭广告 | ").press("back")  # 弹出广告提示框的时候关闭
            self.d.watcher.when("关闭").click()
            self.d.watcher.when("关闭弹框").click()
            self.d.watcher.when("同意").click()  # 隐私协议弹框
            self.d.watcher.when("稍后再说").click()
            self.d.watcher.when("取消").click()
            self.d.watcher.when("返回").click()
            self.d.watcher("ANR").when(xpath="ANR").click()
            self.d.watcher.start()
        except Exception as e:
            print("start_monitor_global_window is exception!" + e)
            raise e

    def stop_monitor_global_window(self):
        """停止全局监测提示框"""
        self.d.watcher.stop()
        self.d.watcher.remove()

    def test_case_reset(self):
        """测试动作前的重置操作"""
        pass

    def _start_test(self):
        """开始测试"""
        self.start_monitor_global_window()
        self.test_case_reset()  # 测试前重置动作不加入视频
        if self.enable_record:
            t = threading.Thread(target=screenrecord.record_start,
                                 args=(self.record_timeout, self.save_file_name, self.camera_type))  # 视频录制功能
            t.start()
        if self.enable_record and self.time_before_record > 0:
            time.sleep(self.time_before_record)  # 置前录制时间

    def _end_test(self):
        """结束测试"""
        if self.enable_record:
            if self.time_after_stop_record > 0:  # 置后结束录制时间
                time.sleep(self.time_after_stop_record)
            screenrecord.record_stop(self.camera_type)
        self.stop_monitor_global_window()
        try:
            while not self.test_completion.wait(timeout=1):
                print(self.test_completion.is_set())
        finally:
            print("test_case is completion")
            self.test_completion.clear()

        self.auto_analyse_video()

    def test_case(self):
        """开始测试--流程方法"""
        try:
            self._start_test()  # 开始测试
            self.test_action()  # 测试
            self._end_test()    # 结束测试
            return True
        except Exception as e:
            self.test_completion.set()
            self._end_test()  # 单次报异常，结束这次测试
            print("{} test_case is exception!".format(self.tag, e))
            # raise e

    def auto_analyse_video(self, timeout=10):
        """
        自动根据视频预测模型分析得出对应结果
        """
        if self.enable_record and self.enable_auto_analyse:
            print("auto parse video start....")
            path = PATH("%s/video/%s" % (os.getcwd(), self.save_file_name))
            path_stagesepx = PATH("%s/%s" % (os.getcwd(), self.stagesepx_frame_blocking_dir))
            if not os.path.isdir(path_stagesepx):
                os.makedirs(path_stagesepx)
            path_video = "%s/%s.mp4" % (path, screenrecord.video_save_name)
            start_time = time.time()
            dead_time = start_time + timeout  # 超时10秒
            while not os.path.exists(path_video) and time.time() < dead_time:
                time.sleep(1)
            print("path_video exists:{}".format(os.path.exists(path_video)))
            name_model = self.save_file_name
            path_model = "%s/%s" % (path_stagesepx, name_model)
            print("auto parse video_model path:{}".format(path_model))
            if os.path.exists("%s/%s.h5" % (path_model, name_model)):
                result = stagesepx_utils.result_get(path_video, path_model, name_model)
                self.calculate_video_time(result)
            else:
                print("please setting video pre model!!")
            print("auto parse video completion....")

    def calculate_video_time(self, _result_get: ClassifierResult):
        """计算视频预测模型中的时间"""
        # stagesepx_utils.calculate(_result_get, "1", "3")
        pass

    def test_action(self):
        pass
