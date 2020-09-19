from numbers import Number
import math
from m5stack import *
from m5ui import *
from uiflow import *
import hat
import urequests
import time
import unit
import hat
from easyIO import *

'''
Setup values
'''
setScreenColor(0xffffff)
ncir0 = unit.get(unit.NCIR, unit.PORTA)
#ncir0 = hat.get(hat.NCIR)
hat_spk0 = hat.get(hat.SPEAKER)
Record = None
Current = None
post_value = None
TempMin = None
TempMax = None
svr_url = 'https://api.asksensors.com/write/A7cQsoPEtMOrWwBnMoEO6Sbta27HiIxw'  # server url
hat_spk0.setVolume(0)  # speaker volume


'''
FUNCTIONS
'''


# sound buzzer
def sound_beep(isNormal):
    if isNormal:
        for i in range(2):
            digitalWrite(33, 1)
            wait(0.075)
            digitalWrite(33, 0)
            wait(0.075)
    else:
        for i in range(3):
            for j in range(2):
                digitalWrite(33, 1)
                wait(0.3)
                digitalWrite(33, 0)
                wait(0.3)


# sound speaker
def sound_spk(vol, hertz):
    hat_spk0.setVolume(vol)
    hat_spk0.sing(262, 1/16)
    hat_spk0.sing(hertz, 1/2)
    hat_spk0.setVolume(0)
    hat_spk0.sing(262, 1/16)
    return None


# record
def record_temp():
    # digitalWrite(33, 1)
    # wait(0.1)
    # digitalWrite(33, 0)
    label0.setText(str(""))
    label1.setText(str(""))
    label2 = M5TextBox(50, 20, "Mengukur ...",
                       lcd.FONT_DejaVu18, 0x275ea8, rotate=90)
    wait_ms(1500)
    current_temp = 2.2 + ncir0.temperature  # kenapa ditambah 2.2 ni
    return current_temp


# check result
def check_result(result):
    isNormal = True
    # normal
    if(result < 37.5):
        setScreenColor(0x14e070)
        isNormal = True
    else:
        setScreenColor(0xff0000)
        isNormal = False
    return isNormal


# post result
def post_result(Record, svr_url):
    post_value = (str('?module4=') + str(Record))
    post_value = (str(svr_url) + str(post_value))
    try:
        req = urequests.request(method='GET', url=post_value)  # post ke server
    except:  # catch error
        pass
        # title0.setBgColor(0xff0000)
    pass


# event handler when button A pressed
def event_handler():

    global Record, svr_url
    Record = record_temp()
    isNormal = check_result(Record)

    label2.setText('' + str(Record) + ' celcius')
    # sound_beep(isNormal) #BUZZER MODE
    # TODO speaker mode
    if(isNormal):
        for i in range(2):
            sound_spk(0.5, 440)
            wait(0.175)
    else:
        for i in range(4):
            sound_spk(10, 262)
            wait(0.2)

    wait(2)
    label0.setText(str(""))
    setScreenColor(0xffffff)
    post_result(Record, svr_url)


'''
Main Process
'''
# btnA.wasPressed(event_handler)  # define event handler
isConfig = True
while(isConfig):

while True:

    label0 = M5TextBox(60, 0, "    Jarak Ukur",
                       lcd.FONT_DejaVu18, 0x275ea8, rotate=90)
    label1 = M5TextBox(35, 30, " 10-15 cm",
                       lcd.FONT_DejaVu18, 0x275ea8, rotate=90)
    label2 = M5TextBox(50, 20, "",
                       lcd.FONT_DejaVu18, 0x275ea8, rotate=90)

    Current = ncir0.temperature + 2.2
    # if(Current >=35):

    wait_ms(2)
    # initate record process (sekarang masih pencet button dulu)
