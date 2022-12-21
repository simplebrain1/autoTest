import os
import time

import uiautomator2 as u2

from autoTestScripts.python.scriptUtils.image_match_utils import ImageMatch

command = os.path.join(f"D:\\studioSDK\\ffmpeg-5.0.1-essentials_build\\bin", "ffmpeg.exe")
PATH = lambda p: os.path.abspath(p)

def parse_video(video_path, dst_path):
    cmd = "%s -i %s -r 100 -threads 2 %s" % (command, video_path, dst_path)+"frame-%05d.png"

    return cmd

# def matching_1(self, source, img, threshold=0.8):
#     """在当前页面匹配目标图片
#     :img: 目标图片
#     :threshold: 相似度阈值
#     :return 返回相似度大于阈值的图片信息，例如: {'result': (177, 2153), 'rectangle': ((89, 2079), (89, 2227), (265, 2227), (265, 2079)), 'confidence': 0.7662398815155029, 'time': 0.08855342864990234}
#     """
#     im_source = imread(source)
#     im_target = imread(img)
#     temp = TemplateMatching(im_target, im_source)
#     setattr(temp, 'threshold', threshold)
#     best_match = temp.find_best_result()
#     # if best_match is None:
#     #     raise AssertionError("没有匹配到目标图片")
#     # print("similarity: %s"%best_match["confidence"])
#     return best_match


if __name__ == "__main__":
    d = u2.connect()
    path = PATH("{}/video/".format(os.getcwd()))
    # cmd = parse_video("%s\\%s" % (path, "homeTabDelay_2022-11-03-16-23-52.mp4"), path+"\\")
    # print(cmd)
    # d.sleep(1)
    # os.popen(cmd)
    # print("ffmpeg compeletion")

    # fpath, fname = os.path.split(path+"\\")  # 分离文件名和路径
    for root, dirs, files in os.walk(path+"\\"):
        for file in files:
            print(root+file)
            img_path = root+file
            im = ImageMatch()
            print("start match {}".format(time.time()))
            img = "frame-00668.png"
            print(im.matching_1(img, img_path))
            print("end match {}".format(time.time()))

        # if len(files) > 0 and fname not in files:
            # shutil.copy(src_file, root + "\\" + fname)

