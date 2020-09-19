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


title0 = M5Title(title="NCIR", x=20, fgcolor=0x3d52ff, bgcolor=0xffffff)
label0 = M5TextBox(24, 30, "Text", lcd.FONT_Default, 0x275ea8, rotate=0)
label1 = M5TextBox(0, 115, "Text", lcd.FONT_Default, 0xb42750, rotate=0)
label2 = M5TextBox(0, 129, "Text", lcd.FONT_Default, 0x214e9c, rotate=0)
label3 = M5TextBox(0, 144, "Text", lcd.FONT_Default, 0x209395, rotate=0)
circle0 = M5Circle(10, 38, 5, 0x000000, 0x000000)
rectangle0 = M5Rect(9, 20, 2, 20, 0x000000, 0x000000)
rectangle1 = M5Rect(10, 26, 5, 2, 0x000000, 0x000000)
rectangle2 = M5Rect(10, 20, 5, 2, 0x000000, 0x000000)
rectangle3 = M5Rect(10, 30, 5, 2, 0x000000, 0x000000)


Record = None
Current = None
post_value = None
TempMin = None
TempMax = None
CurY = None
svr_url = None
DisplayMin = None
DispalyMax = None
T_line = None
Y_BASE = None


def buttonA_wasPressed():
    global Record, Current, post_value, TempMin, TempMax, CurY, svr_url, DisplayMin, DispalyMax, T_line, Y_BASE
    Record = Current
    post_value = (str('?module4=') + str(Record))
    post_value = (str(svr_url) + str(post_value))
    if Record < 37.5:
        hat_spk0.sing(262, 2)
    else:
        hat_spk0.sing(523, 4)
    try:
        req = urequests.request(method='GET', url=post_value)
        title0.setBgColor(0x66ff99)
    except:
        title0.setBgColor(0xff0000)
    pass


btnA.wasPressed(buttonA_wasPressed)


Record = None
TempMin = 100
TempMax = -50
CurY = 105
DisplayMin = -10
DispalyMax = 40
T_line = 1
Y_BASE = 95
Current = -10
svr_url = 'https://api.asksensors.com/write/A7cQsoPEtMOrWwBnMoEO6Sbta27HiIxw'
hat_spk0.setVolume(0)
lcd.rect(0, 55, 80, 51, fillcolor=0xffffff)
lcd.line(0, 54, 0, 105, 0x000000)
lcd.line(0, 106, 80, 106, 0x000000)
while True:
    Current = ncir0.temperature
    Current = 2.2 + Current
    label0.setText(str(Current))
    if Current > TempMax:
        TempMax = Current
    if Current < TempMin:
        TempMin = Current
    label1.setText(str((str('MAX:') + str(str(TempMax)))))
    label2.setText(str((str('MIN:') + str(str(TempMin)))))
    label3.setText(str((str('REC:') + str(str(Record)))))
    if Current > DispalyMax:
        Current = DispalyMax
    elif Current < DisplayMin:
        Current = DisplayMin
    CurY = Y_BASE - math.floor(Current)
    lcd.line(T_line, CurY, T_line, 105, 0x3366ff)
    wait_ms(300)
    if T_line > 80:
        lcd.rect(0, 55, 80, 50, fillcolor=0xffffff)
        T_line = 0
    T_line = (T_line if isinstance(T_line, Number) else 0) + 1
    wait_ms(2)
