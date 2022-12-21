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


def push_fpstool_to_device(self):
    path = PATH("{}/shell/fps_info.sh".format(os.getcwd()))
    if not os.path.exists(path):
        print("fps_info.sh is no find")
        return False
    utils.adb(
        "push " + path + " /data/local/tmp").wait()
    self.d.push(path, "/data/local/tmp/")
    print("push fps_info.sh succeed.")
    return True


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
        f.write("应用包名, 场景, 启动/响应时间(s), 标准值 ,时间戳\n{} , {} , {} , {}, {}".format(package, scan, duration, normal, utils.timestamp()))
    else:
        f = open(path_all_test_file, "a")
        f.write("\n{}, {} , {} , {} , {}".format(package, scan, duration, normal, utils.timestamp()))

    f.close()
    print("write_to_csv Completed")


if __name__ == "__main__":
    write_to_csv("TestHomeHistoryClickBootTime.csv", duration="1")
