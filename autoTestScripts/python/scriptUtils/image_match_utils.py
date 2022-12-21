# import uiautomator2 as u2
# from airtest.aircv.aircv import *
# from airtest.aircv.template_matching import *
#
# """airtest图片识别工具类"""
#
#
# class ImageMatch:
#     def __init__(self):
#         self.d = u2.connect()
#
#     def match_img(self, img, threshold=0.8):
#         """图片匹配
#         :img: 图片，APP中截取的图片
#         :threshold: 阈值
#         """
#         best_match = self._img_matching(img, threshold=threshold)
#         try:
#             similarity = best_match["confidence"]
#             print("相似度: %s" % similarity)
#             return similarity
#         except Exception as e:
#             raise RuntimeError(e)
#
#     def touch_img(self, img, threshold=0.8):
#         """根据图片点击
#         :img: 图片，APP中截取的图片
#         :threshold: 阈值
#         """
#         best_match = self._img_matching(img, threshold=threshold)
#         try:
#             self.d.click(*best_match['result'])
#         except Exception as e:
#             raise RuntimeError(e)
#
#     def _img_matching(self, img, threshold=0.8):
#         """在当前页面匹配目标图片
#         :img: 目标图片
#         :threshold: 相似度阈值
#         :return 返回相似度大于阈值的图片信息，例如: {'result': (177, 2153), 'rectangle': ((89, 2079), (89, 2227), (265, 2227), (265, 2079)), 'confidence': 0.7662398815155029, 'time': 0.08855342864990234}
#         """
#         im_source = self.d.screenshot(format='opencv')
#         im_target = imread(img)
#         temp = TemplateMatching(im_target, im_source)
#         setattr(temp, 'threshold', threshold)
#         best_match = temp.find_best_result()
#         if best_match is None:
#             raise AssertionError("没有匹配到目标图片")
#         # print("similarity: %s"%best_match["confidence"])
#         return best_match
#
#
# if __name__ == '__main__':
#     im = ImageMatch()
#     print("start match {}".format(time.time()))
#     img = "vip.png"
#     print(im.match_img(img))
#     print("end match {}".format(time.time()))
#     # im.touch_img(img)
