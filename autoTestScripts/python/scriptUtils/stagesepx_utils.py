import shutil

from stagesepx.classifier.keras import KerasClassifier
from stagesepx.classifier.base import ClassifierResult
from stagesepx.cutter import VideoCutter
from stagesepx.reporter import Reporter
from stagesepx.video import VideoObject
from autoTestScripts.python.scriptUtils import constant
from autoTestScripts.python.scriptUtils import image_compare_utils


# 详细案例使用https://blog.csdn.net/wsc106/article/details/107351675
# 常用参数如下
# param_list = [门限值：threshold, 偏移量：offset, 切分块数：block ]
# param_list = [[0.97, 1, 6], [0.96, 1, 6], [0.96, 1, 8], [0.97, 1, 8]
#               [0.97, 2, 6], [0.96, 2, 6], [0.96, 2, 8], [0.97, 2, 8]
#               [0.97, 3, 6], [0.96, 3, 6], [0.96, 3, 8], [0.97, 3, 8]]


def video_frame_blocking(video_path, model_path):
    """生成稳定帧分区"""
    # 将视频切分成帧
    file_name = video_path  # './video/homeTabDelay_2022-12-02-18-18-01.mp4'
    video = VideoObject(file_name, pre_load=True)
    # 新建帧，计算视频总共有多少帧，每帧多少ms
    video.load_frames()
    # 压缩视频
    cutter = VideoCutter(compress_rate=constant.CONST.stagesepx.compress_rate)
    # 计算每一帧视频的每一个block的ssim和psnr。
    res = cutter.cut(video, block=constant.CONST.stagesepx.block)
    # 计算出判断A帧到B帧之间是稳定还是不稳定
    stable, unstable = res.get_range(threshold=constant.CONST.stagesepx.threshold,
                                     offset=constant.CONST.stagesepx.offset)
    # 把分好类的稳定阶段的图片存本地
    res.pick_and_save(stable, 20, to_dir='%s/stable_frame' % model_path, meaningful_name=True)


def train_model_file(model_path, model_name="model"):
    # 训练模型文件
    cl = KerasClassifier(
        # 训练轮数
        epochs=10,
        # # 保证数据集的分辨率统一性
        # target_size=(1280, 720)
        compress_rate=constant.CONST.stagesepx.compress_rate
    )
    cl.train('%s/stable_frame' % model_path)
    cl.save_model('%s/%s.h5' % (model_path, model_name), overwrite=True)


def result_get(video_path, forecast_result_path, model_path, model_name="model"):
    # # 使用Keras方法进行预测
    cl = KerasClassifier(
        # 在使用时需要保证数据集格式统一（与训练集）。
        compress_rate=constant.CONST.stagesepx.compress_rate
    )
    cl.load_model('%s/%s.h5' % (model_path, model_name))

    # 将视频切分成帧
    file_name = video_path  # './video/homeTabDelay_2022-12-02-18-18-01.mp4'
    video = VideoObject(file_name)
    # 新建帧，计算视频总共有多少帧，每帧多少ms
    video.load_frames()
    # 压缩视频
    # cutter = VideoCutter(compress_rate=constant.CONST.stagesepx.compress_rate)
    cutter = VideoCutter()
    # 计算每一帧视频的每一个block的ssim和psnr。
    res = cutter.cut(video, block=constant.CONST.stagesepx.block)
    # 判断A帧到B帧之间是稳定还是不稳定
    stable, unstable = res.get_range(
        threshold=constant.CONST.stagesepx.threshold,
        offset=constant.CONST.stagesepx.offset
    )
    # 把分好类的稳定阶段的图片存本地
    try:
        shutil.rmtree('%s/forecast_frame_stable' % forecast_result_path)
        shutil.rmtree('%s/forecast_frame_unstable' % forecast_result_path)
    except OSError as e:
        print("Error: %s : %s" % ('/forecast_stable_', e.strerror))
    res.pick_and_save(stable, 20, to_dir='%s/forecast_frame_stable' % forecast_result_path,
                      meaningful_name=True)
    res.pick_and_save(unstable, 40, to_dir='%s/forecast_frame_unstable' % forecast_result_path,
                      meaningful_name=True)
    # 对切分后的稳定区间，进行归类
    classify_result = cl.classify(file_name, stable,
                                  keep_data=True)
    result_dict = classify_result.to_dict()
    # list = result_dict.get("6")
    # length = len(list)
    # list[length-1]
    # 打印结果
    print(result_dict)

    # 输出html报告
    r = Reporter()
    r.draw(classify_result, '%s/result.html' % forecast_result_path)

    return classify_result


def calculate_common(_result_get: ClassifierResult, _start_stage: str, _end_stage: str,
                     _image_path: str = None,
                     _image_parm: dict = None,
                     _first_start_stage: bool = True,
                     _first_end_stage: bool = True):
    # 自动计算视频对应稳定帧阶段的的时间
    """
    :param _result_get: 视频根据预测模式得到的对应帧分析类
    :param _start_stage: 开始帧对应分区下标
    :param _end_stage: 结束帧对应分区下标
    :param _image_path: 图片比对
    :param _image_parm: 图片比对参数
    :param _first_start_stage: 是否开始帧分区帧列表第一个，默认为True
    :param _first_end_stage: 是否结束帧分区帧列表第一个，默认为True
    :return:
    """
    start_frame = None
    end_frame = None
    list_stage_start = _result_get.get_specific_stage_range(_start_stage)
    list_stage_end = _result_get.get_specific_stage_range(_end_stage)
    length_start = len(list_stage_start)
    length_end = len(list_stage_end)
    if length_start > 0:
        if _first_start_stage:
            start_frame = list_stage_start[0][0]
        else:
            start_frame = list_stage_start[-1][0]
    if length_end > 0:
        if _first_end_stage:
            end_frame = list_stage_end[0][0]
        else:
            end_frame = list_stage_end[-1][0]
    print(
        f",length_start:{length_start}+"f",length_end:{length_end}+"f",start_frame:{start_frame}" + f",end_frame:{end_frame}")
    cost = -1
    if start_frame is not None and end_frame is not None:
        cost = end_frame.timestamp - start_frame.timestamp
        print(f"and the cost: {cost}" + f",start_frame:{start_frame}" + f",end_frame:{end_frame}")

    if _image_path is None:
        return cost

    data_list = _result_get.data
    # contain_image (>=0.9.1)
    # 你可以利用模板匹配，对最终结果与你的预期进行对比，从而得知阶段是否与你的期望相符
    # 全自动化的校验可以在此基础上展开
    compare_sim = 0
    compare = None
    if _image_parm is None:
        _image_parm = {'mse': 10.0, 'ssim': 0.97, 'pnsr': 10}
    for i, image_object in enumerate(data_list):
        print("第%d次对比：" % i)
        print(image_object)
        res = image_object.contain_image(
            image_path=_image_path,
            engine_template_scale=(0.1, 1, 10))
        print(res)
        image_result = image_compare_utils.compare_image_ndarray(_image_path, image_object.data)
        # if res['target_sim'] > compare_sim:
        #     compare_sim = res['target_sim']
        #     compare = image_object
        if image_result['mse'] <= _image_parm['mse'] and image_result['ssim'] >= _image_parm['ssim']:
            compare = image_object
            break

    print("通过模型对比获得的时间差为:%s" % cost)
    if start_frame is not None and compare is not None:
        print("图片比对最终获取到的frame_id:%d,时间点为:%f sim: %f" % (compare.frame_id, compare.timestamp, compare_sim))
        print("start_frame:%s" % start_frame)
        cost = compare.timestamp - start_frame.timestamp
        print("图片比对最终获取到的时间差为:%s" % cost)
    return cost


def calculate_splash(_result_get: ClassifierResult, _start_: str, _end_: str,
                     _image_path: str,
                     _image_parm: dict = None,
                     ):
    # 自动计算冷启动闪屏页
    return calculate_common(_result_get, _start_, _end_, _image_path, _image_parm)


def calculate_ui_showed(_result_get: ClassifierResult, _start_stage: str, _end_stage: str,
                        _image_path: str,
                        _image_parm: dict = None,
                        ):
    # 自动计算冷启动ui界面正式显示
    return calculate_common(_result_get, _start_stage, _end_stage, _image_path, _image_parm, _first_end_stage=False)


if __name__ == "__main__":
    path_video = "./video/TestHomeColdBootTime_2022-12-13-11-34-42.mp4"
    name_model = "TestHomeColdBootTime"
    path_model = "./picture/%s" % name_model
    # video_frame_blocking(path_video, path_model)
    # train_model_file(path_model, name_model)  # 预测模型文件生成
    result = result_get(path_video, path_model, path_model, name_model)  # 根据预测模型进行结果自动换算（注：需保持视频录制几本一致）
    calculate_common(result, "1", "3")  # 稳定帧分区时间云计算
