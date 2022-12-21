# coding=utf-8
import os
import time
import subprocess

PATH = lambda p: os.path.abspath(p)


class FFmpegRecorder(object):
    def __init__(self, camera_device="None"):
        self.__restore_ffmpeg()  # 先重置ffmpeg
        self.camera_device = camera_device
        self.command = os.path.join(f"D:\\studioSDK\\ffmpeg-5.0.1-essentials_build\\bin", "ffmpeg.exe")
        if not os.path.exists(self.command):
            self.command = "ffmpeg"  # 需配置环境变量

        self.__ffmpeg_p = None

    def __restore_ffmpeg(self):
        """防止ffmpeg正在录制视频，导致视频设备被占用"""
        os.system("taskkill /im ffmpeg.exe /f")

    def start_record(self, output_file):
        command = "%s -f dshow -i video=\"%s\" -s 1280x720 -vcodec libxvid -acodec aac -r 60 -f mp4 %s" % (
            self.command, self.camera_device, output_file)
        print(command)
        self.__ffmpeg_p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        # subprocess.Popen().send_signal(CTRL_C_EVENT)

    def stop_record(self):
        try:
            if self.__ffmpeg_p is not None:
                self.__ffmpeg_p.stdin.write("q".encode())
                self.__ffmpeg_p.communicate()
            else:
                print("please run start_record() firstly")
        except Exception as e:
            print("TestEducateHomeTabSwitch is exception!".format(e))
            raise e


if __name__ == "__main__":
    # CAMERA_DEVICE = "Integrated Camera"  # 常量， 自行去Windows设备管理器查看
    CAMERA_DEVICE = "e2eSoft iVCam"
    f_obj = FFmpegRecorder(CAMERA_DEVICE)
    f_obj.start_record("cap118.mp4")
    time.sleep(20)  # 录制多久
    f_obj.stop_record()
