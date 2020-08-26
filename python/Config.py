from numbers import Number
from m5stack import *
from m5ui import *
from uiflow import *
from m5mqtt import M5mqtt
import wifiCfg
import time

setScreenColor(0x111111)


m5mqtt = M5mqtt('', 'app.itsmyhealth.id', 1882, 'sens1', 'testing1', 300)


label0 = M5TextBox(52, 9, "Text", lcd.FONT_DefaultSmall, 0xFFFFFF, rotate=90)
label1 = M5TextBox(74, 6, "Text1", lcd.FONT_Default, 0xFFFFFF, rotate=90)
label2 = M5TextBox(34, 7, "Text2", lcd.FONT_DefaultSmall, 0xFFFFFF, rotate=90)
label3 = M5TextBox(17, 8, "text3", lcd.FONT_DefaultSmall, 0xFFFFFF, rotate=90)


MQTTConnection = None
loop_count = None


def configure():
    global MQTTConnection, loop_count
    m5mqtt.publish(str('/server-connection'), str('{"isConnectRequest":true}'))
    label1.setText(str((str('Configurating') + str('.'))))
    label0.setText(
        str((str('Wifi Connection: ') + str((wifiCfg.wlan_sta.isconnected())))))
    label2.setText(str((str('Server connection: ') + str(MQTTConnection))))
    wait_ms(100)
    label1.setText(str((str('Configurating') + str('..'))))
    wait_ms(100)
    label1.setText(str((str('Configurating') + str('...'))))
    wait_ms(100)


def setToStart():
    global MQTTConnection, loop_count
    label0.setText('')
    label1.setText('')
    label2.setText('')
    if not MQTTConnection:
        setScreenColor(0xcc9933)
        label1.setText('Warning:')
        label0.setText('Server not connected')
        label3.setText('Starting offline mode')
    if not (wifiCfg.wlan_sta.isconnected()):
        setScreenColor(0xcc9933)
        label1.setText('Warning:')
        label2.setText('Wifi not connected')
        label3.setText('Starting offline mode')
    if (wifiCfg.wlan_sta.isconnected()) and MQTTConnection:
        setScreenColor(0x33cc00)
        label1.setPosition(45, 25)
        label1.setText('Setup Complete')


def fun__server_response_(topic_data):
    global MQTTConnection, loop_count
    MQTTConnection = True
    pass


m5mqtt.subscribe(str('/server-response'), fun__server_response_)


MQTTConnection = False
setScreenColor(0x339999)
m5mqtt.start()
configure()
loop_count = 0
while not MQTTConnection:
    configure()
    loop_count = (loop_count if isinstance(loop_count, Number) else 0) + 1
    if loop_count > 10:
        break
configure()
wait(1)
setToStart()
