from stagesepx.classifier.keras import KerasClassifier
from stagesepx.classifier.base import ClassifierResult
from stagesepx.cutter import VideoCutter
from stagesepx.reporter import Reporter
from stagesepx.video import VideoObject


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
    cutter = VideoCutter()
    # 计算每一帧视频的每一个block的ssim和psnr。
    res = cutter.cut(video, block=6)
    # 计算出判断A帧到B帧之间是稳定还是不稳定
    stable, unstable = res.get_range(threshold=0.96, offset=3)
    # 把分好类的稳定阶段的图片存本地
    res.pick_and_save(stable, 20, to_dir='%s/stable_frame' % model_path, meaningful_name=True)


def train_model_file(model_path, model_name="model"):
    # 训练模型文件
    cl = KerasClassifier(
        # 训练轮数
        epochs=10,
        # # 保证数据集的分辨率统一性
        # target_size=(1280, 720)
    )
    cl.train('%s/stable_frame' % model_path)
    cl.save_model('%s/%s.h5' % (model_path, model_name), overwrite=True)


def result_get(video_path, model_path, model_name="model"):
    # # 使用Keras方法进行预测
    cl = KerasClassifier()
    cl.load_model('%s/%s.h5' % (model_path, model_name))

    # 将视频切分成帧
    file_name = video_path  # './video/homeTabDelay_2022-12-02-18-18-01.mp4'
    video = VideoObject(file_name)
    # 新建帧，计算视频总共有多少帧，每帧多少ms
    video.load_frames()
    # 压缩视频
    cutter = VideoCutter()
    # 计算每一帧视频的每一个block的ssim和psnr。
    res = cutter.cut(video, block=6)
    # 判断A帧到B帧之间是稳定还是不稳定
    stable, unstable = res.get_range(threshold=0.97)
    # 把分好类的稳定阶段的图片存本地
    res.pick_and_save(stable, 20, to_dir='%s/forecast_frame' % model_path,
                      meaningful_name=True)
    # 对切分后的稳定区间，进行归类
    classify_result = cl.classify(file_name, stable,
                                  keep_data=True)
    result_dict = classify_result.to_dict()

    # 打印结果
    print(result_dict)

    # 输出html报告
    r = Reporter()
    r.draw(classify_result, '%s/result.html' % model_path)

    return classify_result


def calculate(_result_get: ClassifierResult, _start_: str, _end_: str):
    # 自动计算视频对应稳定帧阶段的的时间
    end_frame = _result_get.last(_end_)
    start_frame = _result_get.first(_start_)
    print(f",start_frame:{start_frame}" + f",end_frame:{end_frame}")
    if start_frame is not None and end_frame is not None:
        cost = end_frame.timestamp - start_frame.timestamp
        print(f"and the cost: {cost}" + f",start_frame:{start_frame}" + f",end_frame:{end_frame}")
        return cost
    return -1


if __name__ == "__main__":
    path_video = "./video/TestHomeColdBootTime_2022-12-13-11-34-42.mp4"
    name_model = "TestHomeColdBootTime"
    path_model = "./picture/%s" % name_model
    # video_frame_blocking(path_video, path_model)
    # train_model_file(path_model, name_model)  # 预测模型文件生成
    result = result_get(path_video, path_model, name_model)  # 根据预测模型进行结果自动换算（注：需保持视频录制几本一致）
    calculate(result, "1", "3")  # 稳定帧分区时间云计算
