import csv
import matplotlib.pyplot as plt
import os
import shutil

from autoTestScripts.python.scriptUtils import utils

PATH = lambda p: os.path.abspath(p)


def move_fps_data_to_save(self, save_file_name):
    path = PATH("{}/FpsFiles/".format(os.getcwd()))
    if not os.path.isdir(path):
        os.makedirs(path)
    utils.adb("pull /data/local/tmp/" + save_file_name + " " + path).wait()
    copy_srcfile_to_dst("./shell/fps_info_parse.sh", path)  # 复制解析脚本到目标目录
    print("move_fpsdata_to_save")
    # os.removedirs("FpsFiles")
    # shutil.rmtree("FpsFiles")


def move_perf_data_to_save(save_file_name: str):
    product_model = utils.shell("getprop ro.product.model").stdout.read().decode().replace('\n', '').replace('\r', '')
    tianci_version = utils.shell("cat /vendor/TianciVersion").stdout.read().decode().replace('\n', '').replace('\r', '')
    path = PATH("{}/perfData/{}_{}/{}".format(os.getcwd(), product_model, tianci_version, save_file_name))
    if not os.path.isdir(path):
        os.makedirs(path)
    utils.adb("pull /data/local/perf/" + " " + path).wait()
    print("move_perf_data_to_save")
    return path + "/perf"
    # os.removedirs("FpsFiles")
    # shutil.rmtree("FpsFiles")


def parse_perf_data(path: str, pkg: str,
                    is_foreground_cpu: bool = True,
                    invalid_cpu: float = 0,
                    standard_cpu_baseline: float = 0.5,
                    standard_cpu_warning_line: float = 0.6,
                    standard_cpu_warning_line_percent: float = 0.2,
                    is_foreground_mem: bool = True,
                    standard_mem_baseline: float = 200,
                    standard_mem_warning_line: float = 250,
                    standard_mem_warning_line_percent: float = 0.2,
                    standard_io_baseline: float = 2048,  # 60分钟写入小于2048KB
                    ):
    result_dict = {}
    temp_path = "{}/{}/Final-{}-cpuInfo.csv".format(path, pkg, pkg)
    # 获取cpu
    average_cpu = 0
    warning_line_cnt = 0
    warning_line_percent = 0
    cpu_record_start_time = ""
    cpu_record_end_time = ""
    num = 0
    with open(temp_path,"r",encoding="utf-8") as csv_file:
        read = csv.DictReader(csv_file)
        for row in read:
            total_proc_cpu_usage = float(row['totalProcCpuUsage'])
            # invalid_cpu, 忽略无效数据， 设置这个值可以忽略静止不动的低cpu使用率
            if total_proc_cpu_usage > invalid_cpu:
                if num == 0:
                    cpu_record_start_time = row['writeTime']
                cpu_record_end_time = row['writeTime']
                num += 1
                average_cpu += total_proc_cpu_usage
                if total_proc_cpu_usage >= standard_cpu_warning_line:
                    warning_line_cnt += 1
                print("totalProcCpuUsage %s" % row['totalProcCpuUsage'])
        if num != 0:
            average_cpu = average_cpu / num
            warning_line_percent = warning_line_cnt / num
        result_dict['平均CPU利用率'] = {'test_result': average_cpu,
                                   'standard_value': standard_cpu_baseline,
                                   'comment': "开始记录时间{}，结束记录时间{}".format(cpu_record_start_time,
                                                                         cpu_record_end_time),
                                   }
        if is_foreground_cpu:
            result_dict['CPU超标的比例'] = {'test_result': warning_line_percent,
                                       'standard_value': "超过{}的比例小于{}".format(standard_cpu_warning_line,
                                                                              standard_cpu_warning_line_percent),
                                       'comment': "开始记录时间{}，结束记录时间{}".format(cpu_record_start_time,
                                                                             cpu_record_end_time),
                                       }
        print("average_cpu:{}".format(average_cpu))
        print("warning_line_percent:{}".format(warning_line_percent))

    # 获取内存
    temp_path = "{}/{}/Final-{}-memInfo.csv".format(path, pkg, pkg)
    average_mem = 0
    num = 0
    warning_line_percent = 0
    warning_line_cnt = 0
    mem_record_start_time = ""
    mem_record_end_time = ""
    with open(temp_path) as csv_file:
        read = csv.DictReader(csv_file)
        x = list()
        y = list()
        for row in read:
            if num == 0:
                mem_record_start_time = row['writeTime']
            mem_record_end_time = row['writeTime']
            total_proc_mem_pss = int(row['totalProcMemPss'])
            num += 1
            x.append(num)
            y.append(row['totalProcMemPss'])
            if total_proc_mem_pss >= standard_mem_warning_line:
                warning_line_cnt += 1
            average_mem += total_proc_mem_pss
            print("totalProcMemPss %s" % row['totalProcMemPss'])
        if num != 0:
            average_mem = average_mem / num
            warning_line_percent = warning_line_cnt / num

        plt.plot(x, y)
        plt.savefig('{}/mem_state.jpg'.format(path))
        # plt.show()
        result_dict['平均内存占用'] = {'test_result': average_mem,
                                 'standard_value': standard_mem_baseline,
                                 'comment': "开始记录时间{}，结束记录时间{}".format(mem_record_start_time,
                                                                       mem_record_end_time),
                                 'test_result_file': '{}/mem_state.jpg'.format(path)
                                 }
        if is_foreground_mem:
            result_dict['内存超标比例'] = {'test_result': warning_line_percent,
                                     'standard_value': "超过{}的比例小于{}".format(standard_mem_warning_line,
                                                                            standard_mem_warning_line_percent),
                                     'comment': "开始记录时间{}，结束记录时间{}".format(mem_record_start_time,
                                                                           mem_record_end_time),
                                     }
        print("average_mem:{}".format(average_mem))

    # 获取io
    temp_path = "{}/{}/Final-{}-io.csv".format(path, pkg, pkg)
    total_io = 0
    num = 0
    io_record_start_time = ""
    io_record_end_time = ""
    with open(temp_path) as csv_file:
        read = csv.DictReader(csv_file)
        for row in read:
            if num == 0:
                io_record_start_time = row['writeTime']
            io_record_end_time = row['writeTime']
            write_bytes = int(row['write_bytes'])
            num += 1
            total_io += write_bytes
            print("write_bytes %s" % row['write_bytes'])
        print("total_io:{}".format(total_io))
        result_dict['磁盘写入总量'] = {'test_result': total_io,
                                 'standard_value': standard_io_baseline,
                                 'comment': "开始记录时间{}，结束记录时间{}".format(io_record_start_time,
                                                                       io_record_end_time),
                                 }
        # total_io = total_io / num
    return result_dict


def push_fpstool_to_device(self):
    path = PATH("{}/shell/fps_info.sh".format(os.getcwd()))
    if not os.path.exists(path):
        print("fps_info.sh is no find")
        return False
    utils.adb(
        "push " + path + " /data/local/tmp").wait()
    # self.d.push(path, "/data/local/tmp/")
    print("push fps_info.sh succeed.")
    return True


def force_copy_file_to_dst(srcfile, dst_path):
    if not os.path.isfile(srcfile):
        print("%s not exist!" % srcfile)
    else:
        fpath, fname = os.path.split(srcfile)
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        shutil.copy(srcfile, dst_path + '/' + fname)
        print("copy %s -> %s" % (srcfile, dst_path + '/' + fname))


def copy_srcfile_to_dst(src_file, dst_path):
    """把源文件复制到目标目录"""
    if not os.path.isfile(src_file):
        print("%s not exist!" % (src_file))
    elif not os.path.isdir(dst_path):
        print("%s not exist!" % (dst_path))
    else:
        fpath, fname = os.path.split(src_file)  # 分离文件名和路径
        for root, dirs, files in os.walk(dst_path):
            if len(files) > 0 and fname not in files:
                shutil.copy(src_file, root + "\\" + fname)


def write_fps_file(path_file: object, content: str) -> object:
    f = open(path_file, "a")
    f.write("%s\n" % content)
    f.close()
    print("write_fps_to_csv Completed")


def write_to_csv(save_file, save_dir="resultDatas", all_result_file="AllResult", **kwargs):
    path = PATH("{}/{}/".format(os.getcwd(), save_dir))
    if not os.path.isdir(path):
        os.makedirs(path)
    path_file = PATH("{}/{}".format(path, save_file + ".csv"))
    path_all_test_file = PATH("{}/{}".format(path, all_result_file + ".csv"))
    duration = None
    normal = None
    package = utils.get_current_package_name()
    scan = None
    if kwargs.get("duration") is not None:
        duration = kwargs.get("duration")
    if kwargs.get("scan") is not None:
        scan = kwargs.get("scan")
    print(" kwargs :", kwargs)
    if not os.path.exists(path_file):
        f = open(path_file, "a")
        f.write("RecordTime , PackageName , Activity , BootTime\n{} , {} , {} , {}".format(utils.timestamp(),
                                                                                           utils.get_current_package_name(),
                                                                                           utils.get_current_activity(),
                                                                                           duration))
    else:
        f = open(path_file, "a")
        f.write("\n{}, {} , {} , {}".format(utils.timestamp(), utils.get_current_package_name(),
                                            utils.get_current_activity(), duration))
    # 结果汇总到一个公用文件夹
    if not os.path.exists(path_all_test_file):
        f = open(path_all_test_file, "a")
        f.write("设备型号：,%s" % utils.shell("getprop ro.product.model").stdout.read().decode())
        f.write("系统版本号：,%s" % utils.shell("getprop third.get.driverBase.version").stdout.read().decode())
        f.write("芯片型号：,%s" % utils.shell("getprop ro.product.odm.model").stdout.read().decode())
        f.write(
            "应用包名, 场景, 启动/响应时间(s), 标准值 ,时间戳\n{} , {} , {} , {}, {}".format(package, scan, duration,
                                                                           normal, utils.timestamp()))
    else:
        f = open(path_all_test_file, "a")
        f.write("\n{}, {} , {} , {} , {}".format(package, scan, duration, normal, utils.timestamp()))

    f.close()
    print("write_to_csv Completed")


def save_app_perf_data(save_file, save_dir="resultDatas", all_result_file="AllResult", **kwargs):
    app_info = None
    if kwargs.get("app_info") is not None:
        app_info = kwargs.get("app_info")
    product_model = utils.shell("getprop ro.product.model").stdout.read().decode().replace('\n', '').replace('\r', '')
    tianci_version = utils.shell("cat /vendor/TianciVersion").stdout.read().decode().replace('\n', '').replace('\r', '')
    path = PATH("{}/{}/{}_{}".format(os.getcwd(), save_dir, product_model, tianci_version))
    if not os.path.isdir(path):
        os.makedirs(path)
    path_file = PATH("{}/{}_{}".format(path, save_file, str(app_info.get("versionName", None)) + ".csv"))
    path_all_test_file = PATH("{}/{}_{}".format(path, all_result_file, str(app_info.get("versionName", None)) + ".csv"))
    package = utils.get_current_package_name()
    # 标准值
    standard_value = None
    # 测试类别
    test_type = None
    # 测试子类
    test_subcategories = None
    # 测试内容
    test_content = None
    # 测试结果
    test_result = None
    # 测试结果是否有文件生成，有的话，复制到总结果目录
    test_result_file = None
    # 备注
    comment = ""
    if kwargs.get("standard_value") is not None:
        standard_value = kwargs.get("standard_value")
    if kwargs.get("test_type") is not None:
        test_type = kwargs.get("test_type")
    if kwargs.get("test_subcategories") is not None:
        test_subcategories = kwargs.get("test_subcategories")
    if kwargs.get("test_result") is not None:
        test_result = kwargs.get("test_result")
    if kwargs.get("test_result_file") is not None:
        test_result_file = kwargs.get("test_result_file")
    if kwargs.get("test_content") is not None:
        test_content = kwargs.get("test_content")
    if kwargs.get("comment") is not None:
        comment = kwargs.get("comment")
    print(" kwargs :", kwargs)
    keep_decimal = lambda x, y: round(x, y) if isinstance(x, float) else x
    test_result = keep_decimal(test_result, 3)
    if not os.path.exists(path_file):
        f = open(path_file, "a")
        f.write("RecordTime , PackageName , Activity , Test_Result\n{} , {} , {} , {}".format(
            utils.timestamp(),
            utils.get_current_package_name(),
            utils.get_current_activity(),
            test_result))
    else:
        f = open(path_file, "a")
        f.write("\n{}, {} , {} , {}".format(utils.timestamp(), utils.get_current_package_name(),
                                            utils.get_current_activity(), test_result))
    # 结果汇总到一个公用文件夹
    if test_result_file is not None:
        force_copy_file_to_dst(test_result_file, path)
    if not os.path.exists(path_all_test_file):
        f = open(path_all_test_file, "a")
        f.write("设备型号：,%s\n" % product_model)
        f.write("系统版本号：,%s\n" % utils.shell("getprop third.get.driverBase.version").stdout
                .read().decode().replace('\n', '').replace('\r', ''))
        f.write("应用大小：,%f MB\n" % (app_info.get("size", 0) / 1024 / 1024))
        f.write("应用versionName：,%s\n" % app_info.get("versionName", None))
        f.write("应用versionCode：,%s\n" % str(app_info.get("versionCode", None)))
        f.write(
            "应用包名, 分类, 测试项, 场景, 测试结果, 标准值 ,测试时间, 备注\n{} , {} , {} , {}, {} , {}, {}, {}".format(
                package,
                test_type, test_subcategories, test_content, test_result,
                standard_value, utils.timestamp(), comment))
    else:
        f = open(path_all_test_file, "a")
        f.write("\n{} , {} , {} , {}, {} , {}, {}, {}".format(
            package,
            test_type, test_subcategories, test_content, test_result,
            standard_value, utils.timestamp(), comment))
    f.close()
    print("save_app_perf_data Completed")


if __name__ == "__main__":
    write_to_csv("TestHomeHistoryClickBootTime.csv", duration="1")
