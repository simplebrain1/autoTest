#!/bin/sh

show_help() {
  echo "
Usage: sh fps_info_parse.sh [type]
Describe:fps_info_parse.sh脚本和运行fps_info.sh生成的fps_temp.txt在同一目录下运行即可
安卓系统6.0以上，使用样例：
For example:sh fps_info_parse.sh
安卓系统6.0以下，使用样例：
For example:sh fps_info_parse.sh 1
POSIX options | GNU long options
    type  |    type有值执行surfaceling来抓的数据解析(6.0以上系统)，没值，走默认
    -h   | --help    Display this help and exit
"
}
function checkUsbPath() {
  USB_ALL_PATH=$(cat /proc/mounts | grep -E 'vfat|ntfs' | busybox awk '{print $2}')
  #USB_ALL_PATH=$(cat /proc/mounts | grep -E 'dev/block/data' | busybox awk '{print $2}')
  for usb in $USB_ALL_PATH; do
    echo "usb path is:$usb"
    echo "usb path is111:$usb"
    mkdir $usb/$currentDataTime
    USBPATH=$usb/$currentDataTime
    mkdir $usb/$currentDataTime/temp
    USB_SCREEN_PATH=$usb/$currentDataTime/temp
  done

  if [ "$USBPATH" == "" ]; then
    return 1
  else
    return 0
  fi
}

function checkStartGfx() {
  startParam=$1
  #  echo "checkStartGfx param: $startParam----$2"
  find=$(echo $startParam | grep $2)

  if [[ "$find" != "" ]]; then
    echo "checkStartGfx is find"
    return 0
  else
    #        echo "checkStartGfx is no find"
    return 1
  fi
}

function checkStopGfx() {
  stopParam=$1
  #  echo "checkStopGfx param: $stopParam"
  find=$(echo $stopParam | grep FrameGetEnd)

  if [[ "$find" != "" ]]; then
    echo "checkStopGfx is find"
    return 0
  else
    #        echo "checkStopGfx is no find"
    return 1
  fi
}

#计算帧率，流畅度等帧信息
function calculateFPSDATA() {
  echo "calculateFPSDATA $1--$2--$3--$4--$5--$6--$7"
  if [ $1 != 0 ]; then
    fpsDuration=$6
    echo " fps fpsDuration : $fpsDuration----index:$index-------completedFrameTime:$completedFrameTime"
    if [ $fpsDuration != 0 ]; then
      lastIndex=$index #结束记录帧率的一行
      echo " fps lastIndex : $lastIndex"
      fpsRecordEndTime=$2

      perTime=$(printf "%.2f" $(echo "scale=2; $fpsDuration/$fpsRecordInterval" | bc))
      frameCount=$(expr $lastIndex - $startIndex)
      fps=$(printf "%.2f" $(echo "scale=2; $frameCount/$perTime" | bc))
#      fps=$(printf "%.2f" $(echo "scale=2; $frameCount*60/($frameCount+$fpsDuration)" | bc))
      maxDurationFrameTime=$3
      if [ $maxDurationFrameTime -lt $fpsVsncTime ]; then
        maxDurationFrameTime=$fpsVsncTime
      fi
      if [ $(echo "$maxFps < $fps" | bc) -eq 1 ]; then #帧率最高为60帧（当只有一帧的时候，帧时长可能小于16.67，帧率计算会超出）
        fps=$maxFps
      fi
      sumFps=$(printf "%.2f" $(echo "scale=2; $sumFps + $fps" | bc))                                                                            #`expr $sumFps + $fps`
      SS=$(printf "%.2f" $(echo "scale=2; $fps/$maxFps*$maxFps+$fpsVsncTime/$maxDurationFrameTime*20+(1-$jumpingFrames/$totalFrames)*20" | bc)) #流畅度
      sumSS=$(printf "%.2f" $(echo "scale=2; $sumSS + $SS" | bc))
      SSArray[${#SSArray[@]}]=$SS
      ((sumSample++))


      #计算卡顿数
       tempSS=$(printf "%.2f" $(echo "scale=2; $lastSS-$lastSS*0.5" | bc))
       if [ $lastSS != 0 -a $(echo "$SS < $tempSS" | bc) -eq 1 -a $maxDurationFrameTime -gt $overFrameExceptionTime ]; then
            ((exceptSum++))
        echo "------计算卡顿率except------,lastNum:$lastSS,num:$SS" >>$currentFpsAccordTemp
       fi
      lastSS=$SS

      if [ -z "$TYPE_COMMAND" ]; then

        sumWindowFps=$(printf "%.2f" $(echo "scale=2; $sumWindowFps + $fps" | bc))
        sumWindowSS=$(printf "%.2f" $(echo "scale=2; $sumWindowSS + $SS" | bc))
        windowSSArray[${#windowSSArray[@]}]=$SS
        ((sumWindowSample++))
        windowArray[1]=$sumWindowFps
        windowArray[2]=$sumWindowSS
        windowArray[3]=$sumWindowSample
        windowArray[4]=$windowSSArray
        windowMap["${windowArray[0]}"]="${windowArray[0]},${windowArray[1]},${windowArray[2]},${windowArray[3]},${windowArray[4]}"

        echo "currentWindow:${windowArray[0]},sumWindowFps:${windowArray[1]},sumWindowSS:${windowArray[2]},sumWindowSample:${windowArray[3]}"
        echo "currentWindow:${windowArray[0]},sumFps:$sumFps,sumSS:$sumSS,sumSample:$sumSample"
        echo "per 1s fps : $fps--perTime:$perTime--frameCount:$frameCount--startIndex:$startIndex--endIndex:$lastIndex--fpsRecordStartTime:$fpsRecordStartTime--fpsRecordEndTime:$fpsRecordEndTime--totalFrames:$totalFrames--jumpingFrames:$jumpingFrames--MaxDurationFrameTime:$maxDurationFrameTime" >>$currentFpsAccordTemp
        echo "${windowArray[0]},$fps,$maxDurationFrameTime,$jumpingFrames,$totalFrames,$SS" >>$currentFpsAccord
      else
        echo "sumFps:$sumFps,sumSS:$sumSS,sumSample:$sumSample"
        echo "per 1s fps : $fps--perTime:$perTime--frameCount:$frameCount--startIndex:$startIndex--endIndex:$lastIndex--fpsRecordStartTime:$fpsRecordStartTime--fpsRecordEndTime:$fpsRecordEndTime--totalFrames:$totalFrames--jumpingFrames:$jumpingFrames--MaxDurationFrameTime:$maxDurationFrameTime" >>$currentFpsAccordTemp
        echo "$fps,$maxDurationFrameTime,$jumpingFrames,$totalFrames,$SS" >>$currentFpsAccord
      fi
    fi
  fi
}

#遍历windowMap找到对应 window的信息
function findWindow() {
  length=${#windowMap[@]}
  echo " findWindow length:$length---$1"
  if [ $length == 0 ]; then
    return 0
  fi
  for key in ${!windowMap[*]}; do
    echo "findWindow--${windowMap[$key]}---key:---$key"
    if [ "$1" == "$key" ]; then
      return 1
    fi
  done
  return 0
}

##计算帧率数据初始化数据
#解析dumpsys gfxinfo 信息
function readFpsDataFile() {
  flag=0
  index=0 #每帧下标
  lastWindow=""
  isSkipInWindowChange=0 #0表示跳过
  while read -r line; do
    temp=$line
    #每帧flag
    frameFlag=0
    #      echo "line: $temp"
    currentWindow=""
    viewRootName=""
    if checkStartGfx "$temp" "visibility=0"; then #每一个window
      viewRootName=$temp
      echo " findWindow---viewRootName:$viewRootName"
      #       fi
      #        if checkStartGfx "$temp" "Window:"  #每一个window
      #        then
      length=${#temp}
      endIndex=$(expr $length - 14)
      windowKey=${temp:0:endIndex}
      #          echo " findWindow---windowKey:$windowKey--${#windowKey}--$viewRootName"
      #          if [ ${#windowKey} == "0" ] #无activity
      #          then
      #            windowKey=$viewRootName
      #          fi
      echo " findWindow---windowKey--:$windowKey"

      if findWindow "$windowKey"; then
        echo " findWindow---0"
        currentWindow="$windowKey"

        sumWindowFps=0    #帧率和
        sumWindowSS=0     #流畅度和

        sumWindowSample=0 #采集次数
        windowSSArray=()  #流畅度集合
        windowArray=()    #每个window信息集合  windowArray[0]:currentWindow,windowArray[1]:sumWindowFps,windowArray[2]:sumWindowSS,windowArray[3]:sumWindowSample,,windowArray[4]:windowSSArray
        windowArray[0]=$currentWindow
        windowArray[1]=$sumWindowFps
        windowArray[2]=$sumWindowSS
        windowArray[3]=$sumWindowSample
        windowArray[4]=$windowSSArray
        windowMap["$windowKey"]="${windowArray[0]},${windowArray[1]},${windowArray[2]},${windowArray[3]},${windowArray[4]}"
      else
        echo " findWindow---1"
        targetData=${windowMap[$windowKey]}
        echo " Window is targetData:$targetData"
        windowArray=(${targetData//,/ })
        currentWindow=${windowArray[0]}
        sumWindowFps=${windowArray[1]}
        sumWindowSS=${windowArray[2]}
        sumWindowSample=${windowArray[3]}
        windowSSArray=${windowArray[4]}
        echo " Window is windowArray:${windowArray[0]}--${windowArray[1]}---${windowArray[2]}---${windowArray[3]}---${windowArray[4]}"
      fi

      if [ "$lastWindow" == "$currentWindow" ]; then
        isSkipInWindowChange=1
      else
        isSkipInWindowChange=0
      fi
      echo " findWindow ,isSkipInWindowChange:$isSkipInWindowChange,lastWindow:$lastWindow,currentWindow:$currentWindow"

      lastWindow=$currentWindow

    fi

    if checkStartGfx "$temp" "FrameCompleted"; then
      flag=1
      #        echo $temp >> $currentFileName
      jumpingFrames=0
      totalFrames=0
      firstFrame=0
      MaxDurationFrameTime=0
      lastDurationFrameTime=0 #上一帧的时长
      lastFrameStartTime=0    #上一帧的开始时间
      #每帧开始时间字段
      startFrameTime=0
      #每帧完成时间字段
      completedFrameTime=0
      dumpDurationFrameTime=0 #dump这一的时长
      vsyncOverTimes=0 #超出的额外花费垂直同步脉冲的数量
      invalidBetweenFrameInterval=0 #无效的间隔时间
      continue
    fi

    if checkStopGfx "$temp"; then
      break
    fi

    if [ $flag == 1 ]; then
      if checkStartGfx "$temp" "PROFILEDATA"; then #过滤PROFILEDATA行
#        fpsTempDuration=$(expr $completedFrameTime - $fpsRecordStartTime)
        fpsDuration=$(expr $completedFrameTime - $fpsRecordStartTime) #$vsyncOverTimes #$dumpDurationFrameTime
        echo " invalidBetweenFrameInterval : $invalidBetweenFrameInterval" >>$currentFpsAccordTemp
        fpsDuration=$(expr $fpsDuration - $invalidBetweenFrameInterval)
        if [ $totalFrames -eq 1 -a $fpsDuration -lt $fpsVsncTime ]; then
          flag=0
          echo " filter fps Index : $index"
          continue
        fi
        #计算帧相关信息的方法
        calculateFPSDATA $startFrameTime $completedFrameTime $MaxDurationFrameTime $totalFrames $jumpingFrames $fpsDuration $windowArray

        flag=0
        continue
      fi

      if [ $isSkipInWindowChange == 0 ]; then  #window切换的时候进行过滤
        flag=0
        echo " isSkipInWindowChange" >>$currentFpsAccordTemp
        continue
      fi

      array=(${temp//,/ })
      if [ -n "${array[0]}" ]; then
        frameFlag=${array[0]}
      fi

      if [ $frameFlag != 0 ]; then #过滤flag>0的或空行
        continue
      fi

      if [ -n "${array[1]}" ]; then
        startFrameTime=${array[1]}
      fi

      if [ -n "${array[13]}" ]; then
        completedFrameTime=${array[13]}
      fi

      if [ $fpsRecordStartTime != 0 -a $fpsRecordStartTime -gt $startFrameTime ]; then #过滤可能重叠的帧
        echo " filter fps Index : $index"
        flag=0
        continue
      fi

      #计算帧率(每秒多少帧)
      if [ $firstFrame == 0 ]; then
        echo " firstFrame fps Index : $index--$fpsRecordEndTime--$startFrameTime" >>$currentFpsAccordTemp
        if [ $fpsRecordEndTime != 0 -a $fpsRecordEndTime -gt $startFrameTime ]; then #过滤可能重叠的帧
          flag=0
          continue
        fi
        startIndex=$index
        fpsRecordStartTime=$startFrameTime
        firstFrame=1
      fi

      onceTime=$(expr $completedFrameTime - $startFrameTime) #每帧时长
      if [ $onceTime -gt $MaxDurationFrameTime ]; then #最大帧耗时
        MaxDurationFrameTime=$onceTime
      fi

      #        echo "per Frame index :$index,frameFlag:$frameFlag",time:" $val---$startFrameTime---$completedFrameTime"
      outputVal="$temp$onceTime"
      echo $outputVal >>$currentFileName
      ((index++))
      ((totalFrames++))

      if [ $onceTime -gt $fpsVsncTime ]; then
        ((jumpingFrames++))
      fi

      if [ $lastFrameStartTime != 0 ]; then #两帧的开始时间超过500ms，并且上一帧时长正常，判定为操作延迟，每到间隔500ms情况发生重新计算帧率。
        betweenFrameInterval=$(expr $startFrameTime - $lastFrameStartTime) #两帧间隔
        if [ $betweenFrameInterval -gt $betweenFrameExceptionInterval -a $lastDurationFrameTime -le $fpsVsncTime ]; then
          echo " filter fps Index : $index" >>$currentFpsAccordTemp
          flag=0
          continue
        fi
          if [ $betweenFrameInterval -gt 100000000 -a  $onceTime -le $fpsVsncTime -a $lastDurationFrameTime -le $fpsVsncTime  ]; then
            overBetweenFrameInterval=$(expr $betweenFrameInterval - $fpsVsncTime)
            invalidBetweenFrameInterval=$(expr $invalidBetweenFrameInterval + $overBetweenFrameInterval)

            echo " invalid betweenFrameInterval : $betweenFrameInterval" >>$currentFpsAccordTemp
          fi
      fi

      lastDurationFrameTime=$onceTime
      lastFrameStartTime=$startFrameTime
#      minDurtaionFrameTime=$onceTime
#      if [ $onceTime -lt $fpsVsncTime ]; then
#            minDurtaionFrameTime=$fpsVsncTime
#      fi
#      dumpDurationFrameTime=$(expr $dumpDurationFrameTime + $minDurtaionFrameTime)

#       if [ $onceTime -gt $fpsVsncTime ]; then
#         val=$(expr $onceTime % $fpsVsncTime)
#            if [ $val == 0 ]; then
#                vsyncOverTimes=$(printf "%.0f" $(echo "scale=0; $vsyncOverTimes+($onceTime/$fpsVsncTime)-1" | bc))
#            else
#                vsyncOverTimes=$(printf "%.0f" $(echo "scale=0; $vsyncOverTimes+$onceTime/$fpsVsncTime" | bc))
#            fi
#       fi
#         echo " vsyncOverTimes : $vsyncOverTimes" >>$currentFpsAccordTemp
    fi

  done <$1  #fps_temp.txt
}

##计算帧率数据初始化数据
##解析dumpsys sufacefling数据
function readFpsDataFile2() {
  flag=0
  index=0 #每帧下标
  while read -r line; do
    temp=$line
    #每帧flag
    frameFlag=0
    #      echo "line: $temp"
    if checkStartGfx "$temp" "DumpFrameStart"; then
      flag=1
      #        echo $temp >> $currentFileName
      jumpingFrames=0
      totalFrames=0
      firstFrame=0
      MaxDurationFrameTime=0
      lastDurationFrameTime=0 #上一帧的时长
      lastFrameStartTime=0    #上一帧的开始时间
      #每帧开始时间字段
      startFrameTime=0
      #每帧完成时间字段
      completedFrameTime=0
      lastLine=""
      validNum=10
      continue
    fi

    if checkStopGfx "$temp"; then
      break
    fi

    if [ $flag == 1 ]; then
      if checkStartGfx "$temp" "DumpFrameEnd"; then #过滤PROFILEDATA行
        fpsDuration=$(expr $completedFrameTime - $fpsRecordStartTime)
        if [ $totalFrames -eq 1 -a $fpsDuration -lt $fpsVsncTime ]; then
          flag=0
          echo " filter fps Index : $index"
          continue
        fi
        #计算帧相关信息的方法
        calculateFPSDATA $startFrameTime $completedFrameTime $MaxDurationFrameTime $totalFrames $jumpingFrames $fpsDuration

        flag=0
        continue
      fi

      #	      array="$temp"
      if [ -z "$temp" ]; then #过滤无效数据
          continue
      fi
      array=(${temp//	/ })
      if [ ${array[0]} == 0 -o ${array[0]} == 16666667 -o ${array[0]} == 16666666 ]; then #过滤无效数据
        continue
      fi
      echo "${array[0]}:${array[1]}:${array[2]}"

      if [ -n "$lastLine" ]; then  #上一行不为空的情况下
          lastArray=(${lastLine//	/ })
          tempVaild=$(printf "%.2f" $(echo "scale=2; ${array[1]}/ ${array[0]}" | bc))
#          echo " filter fps tempVaild : $tempVaild"
          if [ $(echo "$validNum < $tempVaild" | bc) -eq 1 ];then
               echo " filter fps tempVaild : $tempVaild"
            continue
          fi

        if [ -n "${lastArray[1]}" ]; then   #两帧中间数值相减即为一帧的时长
          startFrameTime=${lastArray[1]}
        fi

        if [ -n "${array[1]}" ]; then
          completedFrameTime=${array[1]}
        fi

        if [ $fpsRecordStartTime != 0 -a $fpsRecordStartTime -gt $startFrameTime ]; then #过滤可能重叠的帧
          echo " filter fps Index : $index"
          flag=0
          continue
        fi

        #计算帧率(每秒多少帧)
        if [ $firstFrame == 0 ]; then
          echo " firstFrame fps Index : $index--$fpsRecordEndTime--$startFrameTime" >>$currentFpsAccordTemp
          if [ $fpsRecordEndTime != 0 -a $fpsRecordEndTime -gt $startFrameTime ]; then #过滤可能重叠的帧
            flag=0
            continue
          fi
          startIndex=$index
          fpsRecordStartTime=$startFrameTime
          firstFrame=1
        fi

        onceTime=$(expr $completedFrameTime - $startFrameTime) #每帧时长
        if [ $onceTime -gt $MaxDurationFrameTime ]; then #最大帧耗时
          MaxDurationFrameTime=$onceTime
        fi

        #        echo "per Frame index :$index,frameFlag:$frameFlag",time:" $val---$startFrameTime---$completedFrameTime"
        outputVal="$temp$onceTime"
        echo $outputVal >>$currentFileName
        ((index++))
        ((totalFrames++))

        if [ $onceTime -gt $fpsVsncTime ]; then
          ((jumpingFrames++))
        fi

        if [ $lastFrameStartTime != 0 ]; then #两帧的开始时间超过500ms，并且上一帧时长正常，判定为操作延迟，每到间隔500ms情况发生重新计算帧率。
          betweenFrameInterval=$(expr $startFrameTime - $lastFrameStartTime) #两帧间隔
          if [ $betweenFrameInterval -gt $betweenFrameExceptionInterval ]; then
            echo " filter fps Index : $index"
            flag=0
            continue
          fi
        fi

        lastDurationFrameTime=$onceTime
        lastFrameStartTime=$startFrameTime
      fi
      lastLine=$temp
    fi

  done <$1  #fps_temp.txt
}

#求卡顿率
function caculStuckPercent() {
  echo "------计算卡顿率------"
  length=${#SSArray[@]}
#  lastNum=0;
#  for num in "${SSArray[@]}"; do #以这种for打印数组
#    echo $num
##    if [ $lastNum != 0 -a $(echo "$num < $baseSS" | bc) -eq 1 -a $(echo "$lastNum < $baseSS" | bc) -eq 1 ]; then
##      ((exceptSum++))
##      echo "------计算卡顿率except------baseSS:$baseSS,lastNum:$lastNum,num:$num" >>$currentFpsAccordTemp
##    fi
##    lastNum=$num
#
#
#    if [ $(echo "$num < $baseSS" | bc) -eq 1 ]; then  #计算卡顿率
#      ((exceptSum++))
#      echo "------计算卡顿率except------baseSS:$baseSS,lastNum:$lastNum,num:$num" >>$currentFpsAccordTemp
#    fi
#  done

  stuckSum=$(echo "scale=2;$exceptSum / $baseStuckSum" | bc)
  stuckPercent=$(echo "scale=3;$stuckSum / $length" | bc)
  echo "------计算卡顿率------exceptSum:$exceptSum,length:$length,stuckSum:$stuckSum,stuckPercent:$stuckPercent" >>$currentFpsAccordTemp
}

#  -h参数匹配
function matchParm() {
  while :; do
    case $1 in
    -h | --help)
      show_help
      exit 0
      ;;
    --) # End of all options
      shift
      break
      ;;
    *) # no more options. Stop while loop
      break
      ;;
    esac
  done

}

currentDataTime=$(date '+%Y%m%d_%H%M%S') #脚本运行开始时间

matchParm $1    #帮助


TYPE_COMMAND=$1 #兼容6.0以下只能用surfaceling来抓
FPS_FILE_DATA=$2
if [ -z "$FPS_FILE_DATA" ]; then
  FPS_FILE_DATA="fps_temp.txt"
fi
USBPATH=$3     #USB路径
if [ -z "$USBPATH" ]; then
  USBPATH="."
fi
echo "1,------设置记录文件------"
currentFileName="$USBPATH/${currentDataTime}_log.csv"          #本次执行保存文件名
currentFpsAccord="$USBPATH/${currentDataTime}_fps.csv"         #本次执行帧率保存文件名
currentFpsAccordTemp="$USBPATH/${currentDataTime}_fps_tmp.log" #本次执行帧率保存详细临时文件
echo "当前时间：$currentDataTime"
echo "当前文件：$currentFileName"
echo "当前帧率保存文件：$currentFpsAccord"
echo "当前命令类型：$TYPE_COMMAND"
echo "帧数据读取路径：$FPS_FILE_DATA"
echo "帧数据保存路径：$USBPATH"

echo "FPS,MFS,OKT,TotalFrames" >>$currentFpsAccord
echo "Flags,IntendedVsync,Vsync,OldestInputEvent,NewestInputEvent,HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,FrameCompleted,DequeueBufferDuration,QueueBufferDuration,FrameDuration" >>$currentFileName
#帧率相关变量
startIndex=0
lastIndex=0
fpsRecordStartTime=0 #每秒帧率开始时间
fpsRecordEndTime=0   #每秒帧率帧率结束时间
maxFps=60
fpsRecordInterval=1000000000            #1s(单位纳秒)
fpsVsncTime=16670000                    #16.67ms(单位纳秒)
betweenFrameExceptionInterval=500000000 #500ms(单位纳秒)两帧异常时间
overFrameExceptionTime=80000000 #判断卡顿的最大帧耗时阀值

averageFps=0         #平均帧率
avreageSS=0          #平均流畅度分数
#
sumFps=0             #帧率和
sumSS=0              #流畅度和
lastSS=0             #上一次流畅分

sumSample=0          #采集次数
SSArray=()           #流畅度集合

declare -A windowMap #windowMap

stuckPercent=0 #卡顿率
exceptSum=0 #卡顿数

baseSS=0       #流畅分数基线

baseStuckSum=1 ##两次超过基线流畅分定义为一次卡顿

#读文件计算
if [ -z "$TYPE_COMMAND" ]; then
  readFpsDataFile $FPS_FILE_DATA
else
  readFpsDataFile2 $FPS_FILE_DATA
fi

#计算平均帧率、平均流畅分数、卡顿流畅基线分
averageFps=$(echo "scale=2;$sumFps / $sumSample" | bc)

avreageSS=$(echo "scale=2;$sumSS / $sumSample" | bc)

baseSS=$(echo "scale=2;$avreageSS-$avreageSS*0.5" | bc)

#echo "${SSArray[@]}"
echo "$baseSS"

caculStuckPercent #计算卡顿率
echo "averageFps:$averageFps,avreageSS:$avreageSS,stuckPercent:$stuckPercent,stuckSum:$stuckSum" >>$currentFpsAccord

echo "test run is over !!!!!!" >>$currentFileName

echo -n "Confirm exit"
read name
exit
