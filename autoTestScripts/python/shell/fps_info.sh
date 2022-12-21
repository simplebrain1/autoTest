#!/bin/sh

show_help() {
echo "
Usage: sh fps_info.sh totaltime saveFilePath packageName
安卓系统6.0及以上用法:
For example:sh fps_info.sh 120 /data/local/tmp/ com.tianci.movieplatform
安卓系统6.0及以下用法:
For example:sh fps_info.sh 120 /data/local/tmp/ com.tianci.movieplatform/com.coocaa.homepage.vast.HomePageActivity#0 1
POSIX options | GNU long options
    totaltime  |     统计时长，单位为秒
    saveFilePath |   保存文件的目录
    packageName |    采集数据的应用包名（6.0以上是包名）或当前应用界面window名称（6.0以下）
    commandtype |    安卓系统6.0以下输入此参数，采用surfaceflinge采集帧数据
    -h   | --help    Display this help and exit

当前应用界面window名称获取方式：
1、dumpsys SurfaceFlinger --list 中找到对应的window名称，一般是最后一个带#的，比如下面执行“dumpsys SurfaceFlinger --list ”内容，最后一个是“com.tianci.ad/com.tianci.ad.ScreensaverActivity#0”,就是当前的                                             <
Display Root#0
mBelowAppWindowsContainers#0
com.android.server.wm.DisplayContent$TaskStackContainers@225b6f4#0
splitScreenDividerAnchor#0
Stack=0#0
animation background stackId=0#0
Task=1#0
AppWindowToken{b273ef2 token=Token{29da1fd ActivityRecord{e30ce54 u0 com.tianci.movieplatform/com.coocaa.homepage.vast.HomePageActivity t1}}}#0
5024c1f com.tianci.movieplatform/com.coocaa.homepage.vast.HomePageActivity#0
com.tianci.movieplatform/com.coocaa.homepage.vast.HomePageActivity#0
homeAnimationLayer#0
Stack=11#0
animation background stackId=11#0
Task=76#0
AppWindowToken{fb7e2fa token=Token{9b125 ActivityRecord{fa4811c u0 com.tianci.ad/.ScreensaverActivity t76}}}#0
93f4014 com.tianci.ad/com.tianci.ad.ScreensaverActivity#0
com.tianci.ad/com.tianci.ad.ScreensaverActivity#0
animationLayer#0
boostedAnimationLayer#0
mAboveAppWindowsContainers#0
WindowToken{530025f android.os.BinderProxy@33ccafe}#0
aa424ac com.coocaa.lifeassistant#0
mImeWindowsContainers#0
WindowToken{3e24f52 android.os.Binder@1d337dd}#0
Display Overlays#0

注：包名/类名+#？需要全路径，比如“com.tianci.ad/.ScreensaverActivity”不合法，“com.tianci.ad/com.tianci.ad.ScreensaverActivity#0”合法
"
}


function checkUsbPath(){
	USB_ALL_PATH=$(cat /proc/mounts | grep -E 'vfat|ntfs' | busybox awk '{print $2}')
	#USB_ALL_PATH=$(cat /proc/mounts | grep -E 'dev/block/data' | busybox awk '{print $2}')
	for usb in $USB_ALL_PATH
	do
		echo "usb path is:$usb"
		echo "usb path is111:$usb"
			mkdir $usb/$currentDataTime
			USBPATH=$usb/$currentDataTime
			mkdir $usb/$currentDataTime/temp
			USB_SCREEN_PATH=$usb/$currentDataTime/temp
	done
	
	if [ "$USBPATH" == "" ]
	then
		return 1
	else
		return 0
	fi
}

#是否打开了便捷面版
function checkPanelWindow(){
	dumpWindow=$(dumpsys window 2>&1 |grep ccosservice)
	#echo "--->[dump window] ($(echo $dumpWindow |grep ccosservice)), time:$(date '+%Y-%m-%d %H:%M:%S')" >> $currentFileName
	echo "--->[dump window] ($dumpWindow), time:$(date '+%Y-%m-%d %H:%M:%S')" >> $tempFileName
    dumpValue1=$(echo $dumpWindow |grep mCurrentFocus)
	dumpValue2=$(echo $dumpWindow |grep mFocusedWindow)

	if [[ "$dumpValue1" != "" || "$dumpValue2" != "" ]]
	then
		echo "[OK] panel is open, time:$(date '+%Y-%m-%d %H:%M:%S')" >> $tempFileName
		return 0
	else
		echo "[ERROR] panel is close, time:$(date '+%Y-%m-%d %H:%M:%S')" >> $tempFileName
		return 1
	fi
}

#---------------帧率方法 ------------
function checkCurrentPackageName(){
	currentPkg=$(getprop sky.current.apk)
	echo "--->[Current PackageName] ($currentPkg)"
	echo "--->[Current PackageName] ($currentPkg), time:$(date '+%Y-%m-%d %H:%M:%S')" >> $currentFileName
}

function checkStartGfx(){
  startParam=$1
#  echo "checkStartGfx param: $startParam----$2"
  find=$(echo $startParam |grep $2)

    if [[ "$find" != "" ]]
    then
        echo "checkStartGfx is find"
        return 0
    else
#        echo "checkStartGfx is no find"
        return 1
    fi
}

function checkStopGfx(){
  stopParam=$1
#  echo "checkStopGfx param: $stopParam"
  find=$(echo $stopParam |grep hierarchy)

    if [[ "$find" != "" ]]
    then
        echo "checkStopGfx is find"
        return 0
    else 
#        echo "checkStopGfx is no find"
        return 1
    fi
}

#此方法需要打开模式渲染分析开关才有数据（只有帧的阶段时间，不是时间戳）
function doOutputCurrentPkgFpsMethod0(){
  setprop debug.hwui.profile visual_bars
  gfxInfo=$(dumpsys gfxinfo $currentPkg)
  echo "--->[dump gfxinfo] ($gfxInfo), time:$(date '+%Y-%m-%d %H:%M:%S')" > $cacheFileName
  dumpsys SurfaceFlinger --latency-clear #重置

  flag=0
  while read -r line
    do
      temp=$line
      echo "line: $temp"
      if checkStartGfx "$temp" "Execute"
      then
        flag=1
        continue
      fi

      if checkStopGfx "$temp"
      then
        break
      fi

#	  echo "line: $flag"
      if [ $flag == 1 ]
      then
          echo $temp >> $currentFileName
      fi

    done < $cacheFileName
}

#此方法可以输出帧详细阶段时间戳安卓6.0以上才有
#Flags,IntendedVsync,Vsync,OldestInputEvent,NewestInputEvent,HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,FrameCompleted,DequeueBufferDuration,QueueBufferDuration,
#帧时长 = FrameCompleted - IntendedVsync
function doOutputCurrentPkgFpsMethod1(){
  dumpsys gfxinfo $currentPkg reset #重置
	sleep 1
  gfxInfo=$(dumpsys gfxinfo $currentPkg framestats)
  echo "--->[dump gfxinfo] ($gfxInfo), time:$(date '+%Y-%m-%d %H:%M:%S')" >> $tempFileName
}

#此方法可以dumpsys SurfaceFlinger获取
function doOutputCurrentPkgFpsMethod2(){
 dumpsys SurfaceFlinger --latency-clear #重置
 sleep 1
 echo "DumpFrameStart" >> $tempFileName
 gfxInfo=$(dumpsys SurfaceFlinger --latency $currentPkg)
 echo "$gfxInfo" >> $tempFileName
 echo "DumpFrameEnd , time:$(date '+%Y-%m-%d %H:%M:%S')" >> $tempFileName
}


#  -h参数匹配
function matchParm() {
while :
do
    case $1 in
        -h | --help)
            show_help
            exit 0
            ;;
        --) # End of all options
            shift
            break
            ;;
        *)  # no more options. Stop while loop
            break
            ;;
    esac
done

}





currentDataTime=$(date '+%Y%m%d_%H%M%S')  #脚本运行开始时间

matchParm $1  #帮助

echo "0,------检查USB PATH------"
countMax=$1 #执行总的时间（秒）
USBPATH=$2  #USB路径
#USB_SCREEN_PATH=$3  #缓存文件路径
TOP_PACKAGENAME=$3 #测试的包名
TYPE_COMMAND=$4  #是否执行dumpsys surfaceFling获取帧信息，默认通过gfxinfo拿





#USB_TRACE_PATH=""  #trace路径
#if checkUsbPath
#then
#	echo "usb path is:$USBPATH"
#	echo "usb temp path is:$USB_SCREEN_PATH"
#else
#	echo -n "Please insert USB disk!!!!!!"
#	read name
#	exit
#fi

echo "1,------设置记录文件------"
#currentFileName="$USBPATH/${currentDataTime}_log.log" #本次执行保存文件名
#cacheFileName="$USB_SCREEN_PATH/${currentDataTime}_cache.txt" #本次执行保存文件名（不追加）
mkdir -p $USBPATH/$currentDataTime
SAVEPATH=$USBPATH/$currentDataTime
tempFileName="$SAVEPATH/fps_temp.txt" #本次执行保存文件名（追加，做对比用）
echo "当前时间：$currentDataTime"
echo "当前文件：$tempFileName"
echo "当前输入应用包名：$TOP_PACKAGENAME"
echo "当前执行命令类型：$TYPE_COMMAND"



currentPkg="" #$(getprop sky.current.apk)  #获取包名
currentCls=$(getprop sky.current.actname)  #获取类名
echo "--->[Current PackageName] ($currentPkg),--->[Current ClassName]($currentCls)----PID:$$"
#检查是否当前是便捷面版，是直接抓面版的帧信息
if checkPanelWindow
then
  currentPkg="com.coocaa.os.ccosservice"
  currentCls=""
fi
if [[ "$currentPkg" == "" ]]
then
  currentPkg=$TOP_PACKAGENAME
fi
echo "PID:$$--->[Current PackageName] ($currentPkg),--->[Current ClassName]($currentCls),FrameDuration is FrameTotalTime(units ns),time :$(date '+%Y-%m-%d %H:%M:%S')" >> tempFileName


echo "2,------开始执行帧获取------->[Current PackageName] ($currentPkg)--->[Current ClassName]($currentCls)"
countNum=0
 echo "Flags,IntendedVsync,Vsync,OldestInputEvent,NewestInputEvent,HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,FrameCompleted,DequeueBufferDuration,QueueBufferDuration,FrameDuration" >>tempFileName
while [ $countNum -lt $countMax ]
do
  if [ -z "$TYPE_COMMAND" ]
  then
	  doOutputCurrentPkgFpsMethod1
	else
	  doOutputCurrentPkgFpsMethod2
	fi

	((countNum++))
	echo "countNum : $countNum"
done

#echo "test run is over !!!!!!" >> $currentFileName
echo "FrameGetEnd test run is over !!!!!!" >> $tempFileName


echo -n "Confirm exit"
read name
exit


