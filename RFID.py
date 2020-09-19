'''
Import module:
Terdapat library yang khusus digunakan pada sensor M5Stack.
Dalam pengembangan mungkin akan muncul notifikasi error 'Unable to Import' karena
modul yang digunakan tidak tersedia pada library python umum.
'''
from m5stack import *
from m5ui import *
from uiflow import *
import time
import unit
from m5mqtt import M5mqtt
import wifiCfg
import time
import math
from easyIO import *
import urequests
import espnow


'''
Global Variables:
Pada aplikasi micropython untuk sensor M5Stack, penggunaan variable global harus dinyatakan secara eksplisit.
'''
MQTTConnection = False
loop_count = None
rtc = machine.RTC()
mo_list = ["Jan", "Feb", "Mar", "Apr", "May",
           "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MAC_ADDR = espnow.get_mac_addr()
# MQ_TOPIC = "v1/devices/me/telemetry"
MQ_TOPIC = "/sensor/v1/" + str(MAC_ADDR)
MQ_SVR = 'app.itsmyhealth.id'  # server url
rfid0 = unit.get(unit.RFID, unit.PORTA)
# str(rfid0.readBlockStr(1))
sub_msg = None
offline_records = {}  # Dictionary dengan key = index, value = message payload berisi data rekaman suhu yang direkam saat offline mode

'''
Configuration Function Group:

1. configure():
Memulai prosedur konfigurasi dengan memeriksa koneksi internet (WIFI) dan koneksi kepada server melalui MQTT

2. setToStart():
Setelah prosedur konfigurasi selesai, menampilkan status koneksi dan menginisiasi offline mode atau online mode sesuai status koneksi

3. fun__server_response_(topic_data):
Overriding function untuk menerima MQTT message dari server. Jika menerima message berarti server terhubung, dan status MQTTConnection diubah menjadi True
Message dari server disimpanpada variabel global sub_msg, dimana message string akan diparse untuk mengambil informasi waktu dan tanggal.

4. check_offline_records():
Memeriksa apakah terdapat data tersimpan pada variabel dictionary offline_records. Fungsi ini di inisiasi jika pemeriksaan koneksi server dan internet berhasil.

'''


def check_offline_records():
    global offline_records
    if(len(offline_records) > 0):
        return True
    else:
        return False


def setToStart():
    global MQTTConnection
    label0.setText('')
    label1.setText('')
    label2.setText('')
    if not MQTTConnection:
        setScreenColor(0xcc9933)
        label0.setText('Warning:')
        label1.setText('Server not connected')
        label3.setText('Starting offline mode')
    if not (wifiCfg.wlan_sta.isconnected()):
        setScreenColor(0xcc9933)
        label0.setText('Warning:')
        label2.setText('Wifi not connected')
        label3.setText('Starting offline mode')
    if (wifiCfg.wlan_sta.isconnected()) and MQTTConnection:
        setScreenColor(0x33cc00)
        label0.setPosition(45, 25)

        global sub_msg, rtc
        datetime = sub_msg.split(",")[1]
        d = datetime.split(":")
        rtc.datetime((int(d[3]), int(d[2]), int(d[1]), 0,
                      int(d[4]), int(d[5]), int(d[6]), int(d[7])))
        label1.setText('Setup Complete')


def fun__server_response_(topic_data):
    global MQTTConnection, sub_msg
    MQTTConnection = True
    sub_msg = topic_data
    pass


def configure():
    global MQTTConnection, loop_count, label0, label2, label1
    mqttSvr.publish(str('/sensor/v1/server-connection'),
                    str('{"isConnectRequest":true}'))

    label0 = M5TextBox(8, 49, "Starting Configuration.",
                       lcd.FONT_DejaVu24, 0xFFFFFF, rotate=0)
    label1 = M5TextBox(10, 107, "Wifi Connection: ",
                       lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
    if(wifiCfg.wlan_sta.isconnected()):
        label1.setText(str(''))
        label1.setText(str('Wifi Connection: Connected'))

    label2 = M5TextBox(10, 153, "Server Connection: ",
                       lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
    if(MQTTConnection == True):
        label2.setText(str(''))
        label2.setText(str('Server connection: Connected'))

    wait(0.1)
    label0.setText(str((str('Starting Configuration') + str('..'))))
    wait(0.1)
    label0.setText(str((str('Starting Configuration') + str('...'))))
    wait(0.1)
    label0 = M5TextBox(8, 49, "Starting Configuration.",
                       lcd.FONT_DejaVu24, 0xFFFFFF, rotate=0)
    wait(1)


'''
General Function Group:
1. check_offline_records():
Memeriksa apakah terdapat data tersimpan pada variabel dictionary offline_records. Fungsi ini di inisiasi jika pemeriksaan koneksi server dan internet berhasil.

2. check_result(result):
Memeriksa apakah hasil perekaman suhu diatas batas normal

3. publish_result(Record, MQ_SVR, isNormal):
Menyusun hasil perekaman suhu kedalam message payload, dan mempublikasikan message payload sebagai MQTT Message

4. offline_publisher(msg):
Mempublikasikan pesan yang sebelumnya tersimpan sebagai offline record
'''


def offline_publisher(msg):
    global m5mqtt, mqttSvr
    mqttSvr.publish(str(MQ_TOPIC), msg)


def publish_result(dataSuhu, MQ_SVR, isNormal, userName):
    global m5mqtt, MAC_ADDR, rtc, mo_list, mqttSvr

    # m5mqtt = M5mqtt('', MQ_SVR, 1883, 'Y1RmDk5xNj1C5KfyxRLG', None, 300)
    # m5mqtt.start()
    ts = rtc.datetime()
    # format to '{:%d:%m:%Y:%H:%M:%S:%f:}'
    ts = str(ts[2]) + ":" + str(mo_list[int(ts[1]-1)]) + ":" + str(ts[0]) + \
        ":" + str(ts[4]) + ":" + str(ts[5]) + ":" + \
        str(ts[6]) + ":" + str(ts[7])
    msg = str('{"sensor_mac_addr": "') + str(MAC_ADDR) + str('", "time_stamp":"') + str(ts) + str(
        '", "temperature": ') + str(dataSuhu) + str(', "isAlert":') + str(isNormal == False) + str('}')
    # m5mqtt.publish(str('v1/devices/me/telemetry'), str(msg))
    # m5mqtt.publish(str('v1/devices/me/telemetry'), str('{"temperature":29}'))

    mqttSvr.publish(str(MQ_TOPIC), msg)
    wait(2)

    # mqttSvr = M5mqtt('', 'app.itsmyhealth.id', 1882, 'sens1', 'testing1', 300)
    # mqttSvr.start()
    mqttSvr.publish(str('/sensor/v1/server-connection'),
                    str("{'isConnectRequest':true}"))
    pass


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


'''
Configuration process:
Bagian ini dijalankan saat memulai proses konfigurasi.
'''
mqttSvr = M5mqtt('', 'app.itsmyhealth.id', 1882, 'sens1', 'testing1', 300)
mqttSvr.subscribe(str('/server-response'), fun__server_response_)
mqttSvr.start()
label0 = M5TextBox(8, 49, "",
                   lcd.FONT_DejaVu24, 0xFFFFFF, rotate=0)
label1 = M5TextBox(10, 107, "",
                   lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label2 = M5TextBox(10, 153, "",
                   lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label3 = M5TextBox(8, 104, "", lcd.FONT_DejaVu24, 0xFFFFFF, rotate=0)
setScreenColor(0x111111)
title0 = M5Title(title="BIKUN Smiling Thermometer :)",
                 x=50, fgcolor=0x363232, bgcolor=0xf2ff00)
setScreenColor(0x339999)

configure()
loop_count = 0
while not MQTTConnection:
    configure()
    loop_count += 1
    if loop_count > 10:
        break
    wait(1)
configure()
wait(1)
setToStart()
wait(1)


setScreenColor(0x222222)
ncir0 = unit.get(unit.NCIR, unit.PORTA)
rfid0 = unit.get(unit.RFID, unit.PORTA)


lblWelcome = M5TextBox(25, 108, "Please Tap Your Card",
                       lcd.FONT_DejaVu24, 0xFFFFFF, rotate=0)
title0 = M5Title(title="BIKUN Smiling Thermometer :)",
                 x=50, fgcolor=0x363232, bgcolor=0xf2ff00)
lblGreeting = M5TextBox(
    25, 34, "Hello ", lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
dataName = M5TextBox(85, 35, "-", lcd.FONT_DejaVu18, 0xe4165e, rotate=0)
labelMin = M5TextBox(23, 209, "Min:", lcd.FONT_Default, 0xFFFFFF, rotate=0)
dataMin = M5TextBox(57, 209, "-", lcd.FONT_Default, 0xFFFFFF, rotate=0)
lblMax = M5TextBox(171, 209, "Max:", lcd.FONT_Default, 0xFFFFFF, rotate=0)
dataMax = M5TextBox(215, 209, "-", lcd.FONT_Default, 0xFFFFFF, rotate=0)

minTemp = None
maxTemp = None
dataSuhu = None
isNormal = None

speaker.setVolume(1)
minTemp = 100
maxTemp = 10


'''
Main loop:
Bagian utama proses
'''
while True:
    if rfid0.isCardOn():  # Trigger perekaman suhu dengan deteksi RFID card
        userName = str(rfid0.readBlockStr(1))
        dataName.setText(str(rfid0.readBlockStr(1)))
        lblWelcome.setPosition(x=20)
        rgb.setBrightness(5)
        rgb.setColorAll(0x3333ff)
        lblWelcome.setText('Put your wrist about      2 cm from the sensor')
        wait(3)
        dataSuhu = ncir0.temperature
        for count in range(10):
            dataSuhu = dataSuhu + (ncir0.temperature)
            dataSuhu = dataSuhu / 2
        dataSuhu = dataSuhu + 2
        isNormal = check_result(dataSuhu)
        lblWelcome.setText(
            str((str('Temp: ') + str(((str(dataSuhu) + str(' C')))))))
        if dataSuhu < minTemp:
            minTemp = dataSuhu
            dataMin.setText(str(minTemp))
        if dataSuhu > maxTemp:
            maxTemp = dataSuhu
            dataMax.setText(str(maxTemp))
        if dataSuhu < 37.5:
            lblWelcome.setColor(0x009900)
            rgb.setColorAll(0x009900)
            speaker.sing(220, 1/2)
        else:
            lblWelcome.setColor(0xff0000)
            rgb.setColorAll(0xff0000)
            speaker.sing(889, 2)
            wait(0.5)
            speaker.sing(889, 2)

        # START PUBLISH SEQUENCE
        if(MQTTConnection and wifiCfg.wlan_sta.isconnected()):
            if(check_offline_records() == True):
                # label0 = M5TextBox(60, 0, "Uploading offline records",
                #                    lcd.FONT_DefaultSmall, 0x275ea8, rotate=90)
                # wait(3)
                for i in offline_records.values():
                    offline_publisher(i)
                offline_records = {}
            publish_result(dataSuhu, MQ_SVR, isNormal, userName)
            wait(5)
        else:
            ts = "OFFLINE MODE"
            msg = str('{"sensor_mac_addr": "') + str(MAC_ADDR) + str('", "time_stamp":"') + str(ts) + str(
                '", "temperature": ') + str(dataSuhu) + str(', "isAlert":') + str(isNormal == False) + str('}')

            offline_index = len(offline_records)
            offline_records[offline_index] = msg
            wait(2)

    else:
        lblWelcome.setPosition(x=25)
        lblWelcome.setColor(0xffffff)
        lblWelcome.setText('Please Tap Your Card')
        dataName.setText('')
        rgb.setBrightness(0)
    wait_ms(2)
