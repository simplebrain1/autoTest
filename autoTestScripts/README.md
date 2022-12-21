此自动化脚本主要以酷开主页测试示例为主
gitlab地址：git@gitlab.skysri.com:penghang1210/coocaaautotest.git

一、环境搭建：
1、安装python3.6+以上
2、下载python编程IDE：pythoncharm，具体见：https://coocaa.feishu.cn/wiki/wikcn9QD5ddyX80OAHhdqLxDeMp
3、配置adb环境，并添加环境变量ANDROID_HOME：可以参考：https://blog.csdn.net/loji521/article/details/125040260
4、下载并配置ffmpeg环境，并添加环境变量，下载可见https://coocaa.feishu.cn/wiki/wikcnEghAkUx3lDF9jU8ryzzsbh里介绍
5、下载uiautomator2等工具库包，使用说明见https://github.com/openatx/uiautomator2
6、熟悉stagesepx的使用，可见https://coocaa.feishu.cn/wiki/wikcnEghAkUx3lDF9jU8ryzzsbh
   stagesepx案例示例：详细案例博客：https://blog.csdn.net/wsc106/article/details/107351675
                    抖音启动案例：https://testerhome.com/topics/22215

二、项目结构：
1、利用uiautomator2结合PO设计模式,实现代码逻辑和业务逻辑相分离
   Driver层（如base_page）:完成对webdriver常用方法的二次封装，如：定位元素方法；
   Page层（目录pages）：存放页面对象，通常一个UI界面封装一个对象类，里面编写对应页面操作方法
   Case层(python根目录以test_*的脚本)：调用各个页面对象类，组合业务逻辑、形成测试用例。
2、项目主要目录介绍（base_test也有各个配置项功能注释）：
   a、scriptUtils:工具库目录
   b、shell:存放帧率获取和解析脚本目录
   c、video:存放自动化操作录制视频目录（需要开启录制开关）
   d、resultDatas:存放各个脚本运行后的结果目录（未通过视频分帧技术的结果）
   e、stagesepxResultDatas:存放各个脚本视频分帧对比预测模型后的目录（需要开启自动解析开关，流程已做，需针对各个视频生成预测模型）
   f、picture:各个自动化示例视频预测模型存放目录（可配置）
   g、pages:存入各个页面对象类的目录
   h、FpsFile:帧率脚本相关数据获取生成目录
3、各个测试用例汇部报表生成目录：
   resultDatas目录下的AllResult.csv（文件名可在base_test自定义）

三、主要脚本介绍
1、base_test.py：测试脚本基类，主要是各个脚本公用流程方法定义、主要目录配置及功能开关配置等，详情见脚本内容注释
2、test_main_merge.py:为批量自动化运行各个示例的脚本
3、其它脚本示例都可以单独运行（具体场景可见命名或脚本类tag标签）
   如：test_cold_boot_time_home.py中 self.tag = '主页home冷启动'，表示此测试案例为主页冷启动场景测试，
   其它类似

四、运行前准备
1、需要提前adb连接好测试设备
2、对uiautomator2服务进行检测,可以在cmd命令行执行uiautomator2 check看是否报错，未报错说明uiautomator2环境正常
3、针对待测应用界面控件进行检验修改（如果待测应用界面布局有变化），通过打开weditor进行控件确认
   注：控件确认主要在pages目前下的页面对象类里