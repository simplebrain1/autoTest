import os

from autoTestScripts.python.scriptUtils import utils, file_uitls

PATH = lambda p: os.path.abspath(p)

# 帧率相关变量
start_index = 0
last_index = 0
fps_record_start_time = 0  # 每秒帧率开始时间
fps_record_end_time = 0  # 每秒帧率帧率结束时间
max_fps = 60
fps_record_interval = 1000000000  # 1s(单位纳秒)
fps_vsync_time = 16670000  # 16.67ms(单位纳秒)
between_frame_exception_interval = 500000000  # 500ms(单位纳秒)两帧异常时间
over_frame_exception_time = 80000000  # 判断卡顿的最大帧耗时阀值

average_fps = 0  # 平均帧率
average_ss = 0  # 平均流畅度分数
#
sum_fps = 0  # 帧率和
sum_ss = 0  # 流畅度和
last_ss = 0  # 上一次流畅分

sum_sample = 0  # 采集次数
ss_array = []  # 流畅度集合

stuck_percent = 0  # 卡顿率
except_sum = 0  # 卡顿数
stuck_sum = 0

base_ss = 0  # 流畅分数基线

base_stuck_sum = 1  # 两次超过基线流畅分定义为一次卡顿

window_map = {}  # 字典

index = 0  # 每帧下标

sum_window_fps = 0  # 帧率和
sum_window_ss = 0  # 流畅度和

sum_window_sample = 0  # 采集次数
window_array = []
current_window = None


class FpsResult(object):
    """帧率计算结果类
     average_fps, average_ss, stuck_percent, stuck_num
     """

    def __init__(self):
        self.average_fps = 0  # 平均帧率
        self.average_ss = 0  # 平均流畅分
        self.stuck_percent = 0  # 卡顿率
        self.stuck_num = 0  # 卡顿数


class FpsParse(object):
    def __init__(self, fps_data_dir,
                 type_command=None):
        """
        """
        self.cur_data_time = utils.timestamp()
        self.fps_data_path = "%s/%s" % (fps_data_dir, "fps_temp.txt")
        self.cur_file_name = "%s/%s_log.csv" % (fps_data_dir, self.cur_data_time)  # 本次执行保存文件名
        self.cur_fps_accord = "%s/%s_fps.csv" % (fps_data_dir, self.cur_data_time)  # 本次执行帧率保存文件名
        self.cur_fps_accord_temp = "%s/%s_fps_tmp.log" % (fps_data_dir, self.cur_data_time)  # 本次执行帧率保存详细临时文件
        self.type_command = None
        if type_command is not None:
            self.type_command = type_command
        print("当前时间：%s\n"
              "当前文件：%s\n"
              "当前帧率保存文件：%s\n"
              "当前命令类型：%s\n"
              "帧数据读取路径：%s\n" % (utils.timestamp(), self.cur_file_name, self.cur_fps_accord_temp
                                , self.type_command, self.fps_data_path))
        file_uitls.write_fps_file(self.cur_fps_accord, "FPS,MFS,OKT,TotalFrames\n")
        file_uitls.write_fps_file(self.cur_file_name, "Flags,IntendedVsync,Vsync,OldestInputEvent,NewestInputEvent,"
                                                      "HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,"
                                                      "SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,"
                                                      "FrameCompleted,DequeueBufferDuration,QueueBufferDuration,"
                                                      "FrameDuration\n")

    def parse_action(self) -> FpsResult:
        # 读文件计算
        global average_fps, average_ss, base_ss, sum_fps, sum_ss, sum_sample
        result = FpsResult()
        if self.type_command is None:
            self.read_fps_data_by_gfx()
        else:
            self.read_fps_data_by_surface()

        # 计算平均帧率、平均流畅分数、卡顿流畅基线分
        average_fps = round(sum_fps / sum_sample, 2)

        average_ss = round(sum_ss / sum_sample, 2)

        base_ss = round(average_ss - average_ss * 0.5, 2)

        print(base_ss)

        self.calc_stuck_percent()  # 计算卡顿率
        file_uitls.write_fps_file(self.cur_fps_accord, "averageFps:%s,avreageSS:%s,stuckPercent:%s,stuckSum:%s\n" % (
            average_fps, average_ss, stuck_percent, except_sum / base_stuck_sum))

        file_uitls.write_fps_file(self.cur_file_name, "test run is over !!!!!!")

        result.average_fps = average_fps
        result.average_ss = average_ss
        result.stuck_percent = stuck_percent
        result.stuck_num = except_sum / base_stuck_sum

        return result

    def read_fps_data_by_gfx(self):
        global index, start_index, last_index, fps_record_start_time, window_array, window_map, sum_window_ss, sum_window_sample, sum_window_fps, current_window
        flag = 0
        index = 0  # 每帧下标
        last_window = ""
        is_skip_in_window_change = 0  # 0表示跳过
        f = open(self.fps_data_path, "r")
        for line in f:
            print(line)
            temp = str(line).rstrip()
            # 每帧flag
            frame_flag = 0
            current_window = ""
            if "visibility=0" in temp:  # 每一个window
                print(" findWindow---temp:%s" % temp)

                length = len(temp)
                end_index = length - 15
                window_key = temp[0: end_index]
                print(" findWindow---windowKey--:%s" % window_key)

                if len(window_map) == 0 and window_map.get(window_key) is None:
                    print(" findWindow---0")

                    current_window = window_key

                    sum_window_fps = 0  # 帧率和
                    sum_window_ss = 0  # 流畅度和

                    sum_window_sample = 0  # 采集次数
                    window_array = [current_window, sum_window_fps, sum_window_ss,
                                    sum_window_sample]
                    window_map[window_key] = "%s,%s,%s,%s" % (
                        window_array[0], window_array[1], window_array[2], window_array[3])
                else:
                    print("findWindow---1")
                    if len(window_map) > 0 and window_map.get(window_key) is not None:
                        target_data = window_map.get(window_key)
                        print(" Window is targetData:$targetData")
                        window_array = target_data.split(",")
                        current_window = window_array[0]
                        sum_window_fps = float(window_array[1])
                        sum_window_ss = float(window_array[2])
                        sum_window_sample = float(window_array[3])
                        print(" Window is windowArray:%s--%s---%s---%s" % (
                            current_window, sum_window_fps, sum_window_ss, sum_window_sample))

                if last_window == current_window:
                    is_skip_in_window_change = 1
                else:
                    is_skip_in_window_change = 0
                print(" findWindow ,isSkipInWindowChange:%s,lastWindow:%s,currentWindow:%s" % (
                    is_skip_in_window_change, last_window, current_window))

                last_window = current_window

            if "FrameCompleted" in temp:
                flag = 1
                jumping_frames = 0
                total_frames = 0
                first_frame = 0
                max_duration_frame_time = 0
                last_duration_frame_time = 0  # 上一帧的时长
                last_frame_start_time = 0  # 上一帧的开始时间
                # 每帧开始时间字段
                start_frame_time = 0
                # 每帧完成时间字段
                completed_frame_time = 0
                invalid_between_frame_interval = 0  # 无效的间隔时间
                continue

            if "FrameGetEnd" in temp:
                break

            if flag == 1:
                if "PROFILEDATA" in temp:  # 过滤PROFILEDATA行
                    fps_duration = completed_frame_time - fps_record_start_time  # $vsyncOverTimes #$dumpDurationFrameTime
                    file_uitls.write_fps_file(self.cur_fps_accord_temp,
                                              " invalidBetweenFrameInterval : %s" % invalid_between_frame_interval)
                    fps_duration = fps_duration - invalid_between_frame_interval
                    if total_frames == 1 and fps_duration < fps_vsync_time:
                        flag = 0
                        print(" filter fps Index :".format(index))
                        continue
                    # 计算帧相关信息的方法
                    self.calc_fps_data(start_frame_time, completed_frame_time, max_duration_frame_time, total_frames,
                                       jumping_frames, fps_duration, window_array)

                    flag = 0
                    continue

                if is_skip_in_window_change == 0:  # window切换的时候进行过滤
                    flag = 0
                    file_uitls.write_fps_file(self.cur_fps_accord_temp, " isSkipInWindowChange")
                    continue

                array = temp.split(",")
                print("array:{}".format(array))
                if len(array[0]) > 0:
                    frame_flag = int(array[0])

                print("frameFlag:{}".format(frame_flag))
                if frame_flag != 0:  # 过滤flag>0的或空行
                    print("frameFlag filter")
                    continue

                if len(array[1]) > 0:
                    start_frame_time = int(array[1])

                if len(array[13]):
                    completed_frame_time = int(array[13])

                print("startFrameTime:{},completedFrameTime:{}".format(start_frame_time, completed_frame_time))
                if fps_record_start_time != 0 and fps_record_start_time > start_frame_time:  # 过滤可能重叠的帧
                    print(" filter fps Index : {}".format(index))
                    flag = 0
                    continue

                # 计算帧率(每秒多少帧)
                if first_frame == 0:
                    file_uitls.write_fps_file(self.cur_fps_accord_temp,
                                              " firstFrame fps Index : {}--{}--{}".format(index, fps_record_end_time,
                                                                                          start_frame_time))
                    if fps_record_end_time != 0 and fps_record_end_time > start_frame_time:  # 过滤可能重叠的帧
                        flag = 0
                        continue
                    start_index = index
                    fps_record_start_time = start_frame_time
                    first_frame = 1

                once_time = completed_frame_time - start_frame_time  # 每帧时长
                if once_time > max_duration_frame_time:  # 最大帧耗时
                    max_duration_frame_time = once_time

                output_val = "{}{}".format(temp, once_time)
                file_uitls.write_fps_file(self.cur_file_name, output_val)
                index = index + 1
                total_frames = total_frames + 1

                if once_time > fps_vsync_time:
                    jumping_frames = jumping_frames + 1

                if last_frame_start_time != 0:  # 两帧的开始时间超过500ms，并且上一帧时长正常，判定为操作延迟，每到间隔500ms情况发生重新计算帧率。
                    between_frame_interval = start_frame_time - last_frame_start_time  # 两帧间隔
                    if between_frame_interval > between_frame_exception_interval and last_duration_frame_time < fps_vsync_time:
                        file_uitls.write_fps_file(self.cur_fps_accord_temp, f" filter fps Index : {index}")
                        flag = 0
                        continue
                    if between_frame_interval > 100000000 and once_time < fps_vsync_time and last_duration_frame_time < fps_vsync_time:
                        over_between_frame_interval = between_frame_interval - fps_vsync_time
                        invalid_between_frame_interval = invalid_between_frame_interval + over_between_frame_interval

                        file_uitls.write_fps_file(self.cur_fps_accord_temp,
                                                  " invalid betweenFrameInterval : {}".format(between_frame_interval))

                last_duration_frame_time = once_time
                last_frame_start_time = start_frame_time

        f.close()
        pass

    def read_fps_data_by_surface(self):
        global index, start_index, last_index, fps_record_start_time, window_array, window_map, sum_window_ss, sum_window_sample, sum_window_fps, current_window
        flag = 0
        index = 0  # 每帧下标
        f = open(self.fps_data_path, "r")
        for line in f:
            print(line)
            temp = str(line).rstrip()
            if "DumpFrameStart" in temp:
                flag = 1
                jumping_frames = 0
                total_frames = 0
                first_frame = 0
                max_duration_frame_time = 0
                last_duration_frame_time = 0  # 上一帧的时长
                last_frame_start_time = 0  # 上一帧的开始时间
                # 每帧开始时间字段
                start_frame_time = 0
                # 每帧完成时间字段
                completed_frame_time = 0
                last_line = ""
                valid_num = 10
                continue

            if "FrameGetEnd" in temp:
                break

            if flag == 1:
                if "DumpFrameEnd" in temp:  # 过滤PROFILEDATA行
                    fps_duration = completed_frame_time - fps_record_start_time
                    if total_frames == 1 and fps_duration < fps_vsync_time:
                        flag = 0
                        print(" filter fps Index : {}".format(index))
                        continue
                    # 计算帧相关信息的方法
                    self.calc_fps_data(start_frame_time, completed_frame_time, max_duration_frame_time, total_frames,
                                       jumping_frames, fps_duration, window_array)

                    flag = 0
                    continue

                if len(temp) == 0:  # 过滤无效数据
                    continue

                array = temp.split("\t")
                if int(array[0]) == 0 or int(array[0]) == 16666667 or int(
                        array[0]) == 16666666:  # 过滤无效数据"不同版本系统时间时间数值会有精度区别16666667"
                    continue
                print("{}:{}:{}".format(array[0], array[1], array[2]))

                if len(last_line) > 0:  # 上一行不为空的情况下
                    last_array = last_line.split("\t")
                    temp_vaild = round(int(array[1]) / int(array[0]), 2)
                    if valid_num < temp_vaild:
                        print(" filter fps tempVaild : {}".format(temp_vaild))
                        continue

                    if len(last_array[1]) > 0:  # 两帧中间数值相减即为一帧的时长
                        start_frame_time = int(last_array[1])

                    if len(array[1]) > 0:
                        completed_frame_time = int(array[1])

                    if fps_record_start_time != 0 and fps_record_start_time > start_frame_time:  # 过滤可能重叠的帧
                        print(" filter fps Index : {}".format(index))
                        flag = 0
                        continue

                    # 计算帧率(每秒多少帧)
                    if first_frame == 0:
                        file_uitls.write_fps_file(self.cur_fps_accord_temp,
                                                  " firstFrame fps Index : {}--{}--{}".format(index,
                                                                                              fps_record_end_time,
                                                                                              start_frame_time))
                        if fps_record_end_time != 0 and fps_record_end_time > start_frame_time:  # 过滤可能重叠的帧
                            flag = 0
                            continue
                        start_index = index
                        fps_record_start_time = start_frame_time
                        first_frame = 1

                    once_time = completed_frame_time - start_frame_time  # 每帧时长
                    if once_time > max_duration_frame_time:  # 最大帧耗时
                        max_duration_frame_time = once_time

                    output_val = "{}{}".format(temp, once_time)
                    file_uitls.write_fps_file(self.cur_file_name, output_val)
                    index += 1
                    total_frames += 1

                    if once_time > fps_vsync_time:
                        jumping_frames += 1

                    if last_frame_start_time != 0:  # 两帧的开始时间超过500ms，并且上一帧时长正常，判定为操作延迟，每到间隔500ms情况发生重新计算帧率。
                        between_frame_interval = start_frame_time - last_frame_start_time  # 两帧间隔
                        if between_frame_interval > between_frame_exception_interval:
                            print(" filter fps Index : {}".format(index))
                            flag = 0
                            continue
                    last_duration_frame_time = once_time
                    last_frame_start_time = start_frame_time

                last_line = temp
        f.close()
        pass

    def calc_fps_data(self, start_frame_time, completed_frame_time, max_duration_frame_time, total_frames,
                      jumping_frames,
                      fps_duration, window_array):
        global index, start_index, fps_record_end_time, last_index, sum_fps, sum_ss, sum_sample, last_ss, except_sum, sum_window_fps, sum_window_ss, sum_window_sample, current_window
        print("calculateFPSDATA{}--{}--{}--{}--{}--{}--{}".format(start_frame_time, completed_frame_time,
                                                                  max_duration_frame_time, total_frames, jumping_frames,
                                                                  fps_duration, window_array))
        if start_frame_time != 0:
            print(" fps fpsDuration : {}----index:{}-------completedFrameTime:{}".format(fps_duration, index,
                                                                                         completed_frame_time))
            if fps_duration != 0:
                last_index = index  # 结束记录帧率的一行
                print(" fps lastIndex : {}".format(last_index))
                fps_record_end_time = completed_frame_time

                per_time = round(fps_duration / fps_record_interval, 2)
                frame_count = last_index - start_index
                fps = round(frame_count / per_time, 2)
                #      fps=$(printf "%.2f" $(echo "scale=2; $frameCount*60/($frameCount+$fpsDuration)" | bc))
                # maxDurationFrameTime = MaxDurationFrameTime
                if max_duration_frame_time < fps_vsync_time:
                    max_duration_frame_time = fps_vsync_time
                if max_fps < fps:  # 帧率最高为60帧（当只有一帧的时候，帧时长可能小于16.67，帧率计算会超出）
                    fps = max_fps

                sum_fps = round(sum_fps + fps, 2)  # `expr $sumFps + $fps`
                ss = round(fps / max_fps * max_fps + fps_vsync_time / max_duration_frame_time * 20 + (
                        1 - jumping_frames / total_frames) * 20, 2)  # 流畅度
                sum_ss = sum_ss + ss
                print(len(ss_array))
                ss_array.append(ss)  # [len(SSArray)] = SS
                sum_sample += 1

                # 计算卡顿数
                temp_ss = round(last_ss - last_ss * 0.5, 2)
                if last_ss != 0 and ss < temp_ss and max_duration_frame_time > over_frame_exception_time:
                    except_sum += 1
                    file_uitls.write_fps_file(self.cur_fps_accord_temp,
                                              "------计算卡顿率except------,lastNum:{},num:{}".format(last_ss, ss))
                last_ss = ss

                if self.type_command is None:
                    sum_window_fps = round(sum_window_fps + fps, 2)
                    sum_window_ss = round(sum_window_ss + ss, 2)
                    sum_window_sample += 1
                    if len(window_array) > 0:
                        window_array[1] = sum_window_fps
                        window_array[2] = sum_window_ss
                        window_array[3] = sum_window_sample
                        window_map[window_array[0]] = "{},{},{},{}".format(window_array[0], window_array[1],
                                                                           window_array[2],
                                                                           window_array[3])

                        print(
                            "currentWindow:{},sumWindowFps:{},sumWindowSS:{},sumWindowSample:{}".format(window_array[0],
                                                                                                        window_array[1],
                                                                                                        window_array[2],
                                                                                                        window_array[
                                                                                                            3]))
                        print(
                            "currentWindow:{},sumFps:{},sumSS:{},sumSample:{}".format(window_array[0], sum_fps, sum_ss,
                                                                                      sum_sample))
                    file_uitls.write_fps_file(self.cur_fps_accord_temp,
                                              "per 1s fps : {}--perTime:{}--frameCount:{}--startIndex:{}--endIndex:{"
                                              "}--fpsRecordStartTime:{}--fpsRecordEndTime:{}--totalFrames:{"
                                              "}--jumpingFrames:{}--MaxDurationFrameTime:{} "
                                              .format(fps, per_time, frame_count, start_index, last_index,
                                                      fps_record_start_time,
                                                      fps_record_end_time, total_frames, jumping_frames,
                                                      max_duration_frame_time))
                    file_uitls.write_fps_file(self.cur_fps_accord,
                                              "{},{},{},{},{},{}".format(window_array[0], fps, max_duration_frame_time,
                                                                         jumping_frames, total_frames, ss))
                else:
                    print("sumFps:{},sumSS:{},sumSample:{}".format(sum_fps, sum_ss, sum_sample))
                    file_uitls.write_fps_file(self.cur_fps_accord_temp,
                                              "per 1s fps : {}--perTime:{}--frameCount:{}--startIndex:{}--endIndex:{"
                                              "}--fpsRecordStartTime:{}--fpsRecordEndTime:{}--totalFrames:{"
                                              "}--jumpingFrames:{}--MaxDurationFrameTime:{}"
                                              .format(fps, per_time, frame_count, start_index, last_index,
                                                      fps_record_start_time,
                                                      fps_record_end_time, total_frames, jumping_frames,
                                                      max_duration_frame_time))
                    file_uitls.write_fps_file(self.cur_fps_accord,
                                              "{},{},{},{},{}".format(fps, max_duration_frame_time, jumping_frames,
                                                                      total_frames,
                                                                      ss))
        pass

    def calc_stuck_percent(self):
        global stuck_percent, stuck_sum
        length = len(ss_array)
        stuck_sum = round(except_sum / base_stuck_sum, 2)
        stuck_percent = round(stuck_sum / length, 3)
        file_uitls.write_fps_file(self.cur_fps_accord_temp,
                                  "------计算卡顿率------exceptSum:%s,length:%s,stuckSum:%s,stuckPercent:%s" % (
                                      except_sum, length, stuck_sum, stuck_percent))


if __name__ == "__main__":
    parse = FpsParse(PATH(os.getcwd()), type_command=None)
    fps_result = parse.parse_action()
    print("{}:{}:{}:{}".format(fps_result.average_fps, fps_result.average_ss, fps_result.stuck_percent, fps_result.stuck_num))
