from stagesepx.classifier.keras import KerasClassifier
from autoTestScripts.python.scriptUtils import constant

import get_data
import time
import train_model
import classify_with_model
import sys
import public_fun

if __name__ == '__main__':
    # 当前日期
    date = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    # 切割视频参数。 视频压缩率：compress_rate, 门限值：threshold, 偏移量：offset, block , date
    # 全量

    #compress_rate要与train保持一致，更改compress_rate要重新训练
    compress_rate = constant.CONST.stagesepx.compress_rate
    threshold = constant.CONST.stagesepx.threshold
    param_list = [
                 #[compress_rate, 0.97, 1, 6, date],
                 # [compress_rate, 0.97, 1, 2, date],
                 #
                 # [compress_rate, 0.97, 2, 6, date],
                 # [compress_rate, 0.97, 3, 6, date],
                 # [compress_rate, 0.97, 1, 8, date],
                 # [compress_rate, 0.97, 2, 8, date],
                 # [compress_rate, 0.97, 3, 8, date],
                 # [compress_rate, 0.97, 2, 2, date],
                 # [compress_rate, 0.97, 3, 2, date],
                 #
                 [compress_rate, threshold, None, constant.CONST.stagesepx.block, date],
                 [compress_rate, threshold, 2, constant.CONST.stagesepx.block, date],
            #     [compress_rate, threshold, 1, 8, date],
              #   [compress_rate, threshold, 3, 8, date],

                 # [compress_rate, threshold, 1, 6, date],
                 # [compress_rate, threshold, 2, 6, date],
                 # [compress_rate, threshold, 3, 6, date],
                 # [compress_rate, threshold, 1, 2, date],
                 # [compress_rate, threshold, 2, 2, date],
                 # [compress_rate, threshold, 3, 2, date]
                 #[0.4, 0.96, 2, 2, date],

                  ]

    test_item = {'name': 'TestLocalMediaBootTime', 'splash': '3', 'main_page': '6'}
    test_item = {'name': 'TestSoftSettingClickBootTime', 'splash': '3', 'main_page': '6'}
    test_item_name = test_item['name']
    # 切割视频阶段
    # 训练模型的视频路径
    video_path_for_train = '../videos/train/%s' % test_item_name
    # 切割后的图片，用来人工挑选
    picture_path_after_cutter = '../picture/train/%s' % test_item_name
    # 模型训练阶段
    # 训练模型
    picture_path_for_train = '../picture_for_train/%s' % test_item_name
    # model_file_name = '../model/model_launch_app.h5'
    model_file_name = '../model/%s.h5' % test_item_name

    # 预测阶段
    # 待预测的视频文件
    # video_path_for_forecast = '../videos/forecast_launch_App_all'
    video_path_for_forecast = '../videos/test_forecast/%s' % test_item_name
    forecast_picture_path_after_cutter = '../picture/forecast/%s' % test_item_name
    # 实际结果的csv，用来对比
    actual_result_csv = '../videos/test_forecast/actual_result.csv'
    # 模型对应的闪屏区间和主界面区间
    # forecast_dict = {'splash': '3', 'main_page': '6'}
    # 视频预测
    cl = None

    # 打印参数
    print('训练视频 = %s' % video_path_for_train)
    # print('用于训练模型的多帧图像 = %s' % picture_path_for_train)
    print('模型文件 = %s' % model_file_name)
    print('预测视频 = %s' % video_path_for_forecast)
    print('---------------------------------------------')
    KerasClassifier.MODEL_DENSE = 15
    # 获取键盘输入
    input_list = public_fun.get_keyboard_input()
    #input_list = ['1\n', '2\n', '2\n']
    # 切割视频
    if input_list[0] == '1\n':
        print("制作训练材料")

        param = param_list[0]
        # 切割出来的视频存放地址
        picture_path_temp = 'cr_' + str(param[0]) + '_th_' + str(param[1]) + '_os_' + str(param[2]) + \
                            '_block_' + str(param[3])
        from_movie_2_picture = picture_path_after_cutter + '/' + picture_path_temp

        file_name_list = public_fun.get_mp4file_name(video_path_for_train)
        for i in file_name_list:
            get_data.get_range('train', i, param, from_movie_2_picture)
        sys.exit()
    else:
        print("不制作训练材料")

    if input_list[1] == '1\n':
        print("训练SVM模型")
        train_model.train_model_SVM(compress_rate, picture_path_for_train, model_file_name)
    elif input_list[1] == '2\n':
        train_start = time.time()
        print("训练Keras模型")
        train_model.train_model_Keras(compress_rate, picture_path_for_train, model_file_name)
        print("训练耗时: {:.2f}秒".format(time.time() - train_start))
    else:
        print("不训练模型")

    # 预测结果
    if input_list[2] == '1\n' or input_list[2] == '2\n':
        SVM_or_Keras = input_list[2]
        forecast_start = time.time()
        for param in param_list:
            # 切割出来的视频存放地址
            picture_path_temp = 'cr_' + str(param[0]) + '_th_' + str(param[1]) + '_os_' + str(param[2]) + \
                                '_block_' + str(param[3])
            from_movie_2_picture = forecast_picture_path_after_cutter + '/' + picture_path_temp

            # forecast_result包含1或者多个视频的预测结果，列表的列表
            forecast_result = classify_with_model.calculate_result(cl, SVM_or_Keras, param, from_movie_2_picture,
                                                                   model_file_name, video_path_for_forecast,
                                                                   test_item)
            # 把结果写本地
            # print("实际结果为", forecast_result)

            # 对比预期和实际结果，输出结果到csv
            csv_output = from_movie_2_picture + '/output_' + picture_path_temp + '.csv'
            # csv_output = '../final_result.csv'
            public_fun.process_csv(actual_result_csv, forecast_result, csv_output)
        print("预测耗时: {:.2f}秒".format(time.time() - forecast_start))
    else:
        print("不进行预测")


