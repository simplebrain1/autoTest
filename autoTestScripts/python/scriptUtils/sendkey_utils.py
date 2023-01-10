import time

from autoTestScripts.python.scriptUtils import utils

device_event = "event1"  # None
keycode_enter = "28"


def send_keycode(keycode):
    # cmd = "sendevent /dev/input/%s 1 %s 1 &sendevent /dev/input/%s 0 0 0 &sendevent /dev/input/%s 1 %s 0 &sendevent " \
    #       "/dev/input/%s 0 0 0\n" % (device_event, keycode, device_event, device_event, keycode, device_event)
    # print(cmd)
    # utils.shell("sendevent /dev/input/%s 1 %s 1" % (device_event, keycode)).wait()
    # utils.shell("sendevent /dev/input/%s 0 0 0" % device_event).wait()
    # time.sleep(1)
    # utils.shell("sendevent /dev/input/%s 1 %s 0" % (device_event, keycode)).wait()
    # utils.shell("sendevent /dev/input/%s 0 0 0" % device_event).wait()
    utils.shell("input keyevent 23").wait()

