#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import time

from autoTestScripts.python.scriptUtils import utils
from autoTestScripts.python.scriptUtils.ffmpeg_screenrecord import FFmpegRecorder

'''
需要Android4.4及4.4以上版本，运行脚本后可录制设备上的操作，默认使用手机分辨率，手动设置录制时间。
录制结果存放于当前目录下的video目录下
uiautomator2自带录制api,实测没有生效（暂用这个）
'''

PATH = lambda p: os.path.abspath(p)

flag = False
# CAMERA_DEVICE = "Integrated Camera"  # 常量， 自行去Windows设备管理器查看
CAMERA_DEVICE = "e2eSoft iVCam"
ffmpeg_recorder = FFmpegRecorder(CAMERA_DEVICE)
save_name = "default"
video_save_name = ""    # 解析视频时需要这个名称


def record_stop(camera_type="local"):
    global save_name, video_save_name
    if camera_type == "local":
        while not flag:
            print("Waiting get Video file...")
            time.sleep(1)

        if flag:
            path = PATH("%s/video/%s" % (os.getcwd(), save_name))
            if not os.path.isdir(path):
                os.makedirs(path)
            print("path %s video_save_name %s:" % (path, save_name))
            video_save_name = save_name + "_" + utils.timestamp()
            utils.adb("pull /data/local/tmp/video.mp4 %s" % PATH("%s/%s.mp4" % (path, video_save_name))).wait()
            print("video is exist? {}".format(os.path.exists(PATH("%s/%s.mp4" % (path, video_save_name)))))
            if os.path.exists(PATH("%s/%s.mp4" % (path, video_save_name))):
                command = "ffmpeg -i %s -r 60 %s" % (
                    PATH('%s/%s.mp4' % (path, video_save_name)), PATH('%s/%s.mp4' % (path, "output")))  # 转换60帧视频
                subprocess.Popen(command).wait()
                start_time = time.time()
                dead_time = start_time + 10  # 超时10秒
                while not os.path.exists(PATH('%s/%s.mp4' % (path, "output"))) and time.time() < dead_time:
                    time.sleep(1)
                if os.path.exists(PATH('%s/%s.mp4' % (path, "output"))):
                    os.remove(PATH('%s/%s.mp4' % (path, video_save_name)))
                    os.renames(PATH('%s/%s.mp4' % (path, "output")), PATH('%s/%s.mp4' % (path, video_save_name)))
            print("Completed")
    else:
        ffmpeg_recorder.stop_record()


def record_start(limit_time, video_name="default", camera_type="local"):
    if video_name != "default":
        global save_name, video_save_name
        save_name = video_name
    if camera_type == "local":
        sdk = utils.shell("getprop ro.build.version.sdk").stdout.read().decode()
        sdk = int(sdk)
        if sdk < 19:
            print("sdk version is %s, less than 19!")
            sys.exit(0)
        else:
            global flag
            flag = False
            utils.shell("rm -f /data/local/tmp/video.mp4")
            try:
                _limit_time = int(limit_time) + 1
            except:
                sys.exit(0)

            if 0 < _limit_time <= 180:
                print("record start {}".format(time.time()))
                utils.shell("screenrecord --time-limit %s /data/local/tmp/video.mp4" % limit_time).wait()
                flag = True
                print("record end {} {}".format(time.time(), flag))
            else:
                print("Please set again!")
                sys.exit(0)
    else:
        path = PATH("%s/video/%s" % (os.getcwd(), save_name))
        if not os.path.isdir(path):
            os.makedirs(path)
        video_save_name = save_name + "_" + utils.timestamp()
        output_path = PATH('%s/%s.mp4' % (path, video_save_name))
        ffmpeg_recorder.start_record(output_path)


if __name__ == "__main__":
    record_start(10)
    record_stop("test")
