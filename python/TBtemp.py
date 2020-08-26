from m5stack import *
from m5ui import *
from uiflow import *
from m5mqtt import M5mqtt
import time

setScreenColor(0x111111)


m5mqtt = M5mqtt('', 'app.itsmyhealth.id', 1883,
                'Y1RmDk5xNj1C5KfyxRLG', 'None', 300)


pass2 = None


pass2 = 0
setScreenColor(0xffff66)
m5mqtt.start()
setScreenColor(0x33ff33)
while True:
    setScreenColor(0xff99ff)
    wait(1)
    m5mqtt.publish(str('v1/devices/me/telemetry'), str(
        '{"sensor_mac_addr": "dc:53:60:d8:77:11", "time_stamp": "30-Jul-2020 15:07:10:247769", "temperature": 38.91, "isAlert": false}'))
    setScreenColor(0x3333ff)
    wait(1)
    wait_ms(2)
