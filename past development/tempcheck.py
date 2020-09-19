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

setScreenColor(0xffffff)
ncir0 = unit.get(unit.NCIR, unit.PORTA)

hat_spk0 = hat.get(hat.SPEAKER)


Record = None
Current = None
post_value = None
TempMin = None
TempMax = None
svr_url = 'https://api.asksensors.com/write/A7cQsoPEtMOrWwBnMoEO6Sbta27HiIxw'  # server url
hat_spk0.setVolume(0)  # speaker volume

# record


def record_temp():
    label0.setText(str(""))
    label0.setText(str("      Mengukur ..."))
    wait_ms(1500)
    current_temp = 2.2 + ncir0.temperature  # kenapa ditambah 2.2 ni
    return current_temp


def check_result(result):
    # normal
    if(result < 37.5):
        # bunyi
        # hat_spk0.sing(262, 2) belum bisa berentiin suara
        setScreenColor(0x14e070)
    else:
        # bunyi
        #hat_spk0.sing(523, 4)
        setScreenColor(0xff0000)

    label0.setText('     ' + str(Record) + ' celcius')
    wait_ms(2500)
    label0.setText(str(""))
    setScreenColor(0xffffff)


def post_result(Record, svr_url):
    post_value = (str('?module4=') + str(Record))
    post_value = (str(svr_url) + str(post_value))
    try:
        req = urequests.request(method='GET', url=post_value)  # post ke server
    except:  # catch error
        pass
        # title0.setBgColor(0xff0000)
    pass


def buttonA_wasPressed():
    global Record, svr_url
    Record = record_temp()
    check_result(Record)
    post_result(Record, svr_url)


btnA.wasPressed(buttonA_wasPressed)  # define event handler

while True:
    label0 = M5TextBox(50, 10, "Jarak Ukur\n 10-15 cm",
                       lcd.FONT_Default, 0x275ea8, rotate=90)
    wait_ms(2)
    # initate record process (sekarang masih pencet button dulu)
