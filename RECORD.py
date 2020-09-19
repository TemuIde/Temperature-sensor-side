'''
Import module:
Terdapat library yang khusus digunakan pada sensor M5Stack.
Dalam pengembangan mungkin akan muncul notifikasi error 'Unable to Import' karena
modul yang digunakan tidak tersedia pada library python umum.
'''

from numbers import Number
from m5stack import *
from m5ui import *
from uiflow import *
from m5mqtt import M5mqtt
import wifiCfg
import time
import math
import unit
import hat
from easyIO import *
import urequests
import espnow


'''
Global Variables:
Pada aplikasi micropython untuk sensor M5Stack, penggunaan variable global harus dinyatakan secara eksplisit.
'''
rtc = machine.RTC()  # real time clock
mo_list = ["Jan", "Feb", "Mar", "Apr", "May",
           "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]  # list nama-nama bulan
MQTTConnection = False  # indikator koneksi ke MQTT Server
loop_count = None  # counter penghitung jumlah perekaman data
sub_msg = None  # subscribed message dari server akan disimpan pada variabel ini
ncir0 = unit.get(unit.NCIR, unit.PORTA)  # sensor suhu
#ncir0 = hat.get(hat.NCIR)
hat_spk0 = hat.get(hat.SPEAKER)  # extension speaker
Record = None  # hasil perekaman suhu
MAC_ADDR = espnow.get_mac_addr()  # mac address sensor
MQ_TOPIC = "/sensor/v1/" + str(MAC_ADDR)  # topic message MQTT
MQ_SVR = 'app.itsmyhealth.id'  # server url
hat_spk0.setVolume(0)  # speaker volume
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
'''


def configure():
    global MQTTConnection, loop_count
    mqttSvr.publish(str('/sensor/v1/server-connection'),
                    str('{"isConnectRequest":true}'))
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
    global MQTTConnection
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


'''
General Function Group:
1. check_offline_records():
Memeriksa apakah terdapat data tersimpan pada variabel dictionary offline_records. Fungsi ini di inisiasi jika pemeriksaan koneksi server dan internet berhasil.

2. sound_beep(isNormal):
Menerima parameter boolean isNormal dan menghasilkan suara melalui buzzer. Hanya jika yang digunakan extension buzzer (defaultnya yang digunakan = speaker)

3. sound_spk(vol, hertz):
Menerima parameter volume dan frekuensi dan menghasilkan suara melalui speaker.

4. record_temp():
Menampilkan display pengukuran dan merekam suhu dari sensor.

5. check_result(result):
Memeriksa apakah hasil perekaman suhu diatas batas normal

6. publish_result(Record, MQ_SVR, isNormal):
Menyusun hasil perekaman suhu kedalam message payload, dan mempublikasikan message payload sebagai MQTT Message

7. offline_publisher(msg):
Mempublikasikan pesan yang sebelumnya tersimpan sebagai offline record
'''
# ===>> offline mode function group start


def check_offline_records():
    global offline_records
    if(len(offline_records) > 0):
        return True
    else:
        return False


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
    global label0, label1, label2, label3, ncir0

    label0.setText(str(""))
    label1.setText(str(""))
    label2 = M5TextBox(50, 20, "Mengukur ...",
                       lcd.FONT_DejaVu18, 0x275ea8, rotate=90)
    wait_ms(1500)
    current_temp = 2.2 + ncir0.temperature  # Penambahan offset sebesar 2.2
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
def publish_result(Record, MQ_SVR, isNormal):
    global m5mqtt, MAC_ADDR, rtc, mo_list, mqttSvr

    ts = rtc.datetime()
    # format to '{:%d:%m:%Y:%H:%M:%S:%f:}'
    ts = str(ts[2]) + ":" + str(mo_list[int(ts[1]-1)]) + ":" + str(ts[0]) + \
        ":" + str(ts[4]) + ":" + str(ts[5]) + ":" + \
        str(ts[6]) + ":" + str(ts[7])
    msg = str('{"sensor_mac_addr": "') + str(MAC_ADDR) + str('", "time_stamp":"') + str(ts) + str(
        '", "temperature": ') + str(Record) + str(', "isAlert":') + str(isNormal == False) + str('}')

    mqttSvr.publish(str(MQ_TOPIC), msg)
    wait(2)

    # mqttSvr = M5mqtt('', 'app.itsmyhealth.id', 1882, 'sens1', 'testing1', 300)
    # mqttSvr.start()
    mqttSvr.publish(str('/sensor/v1/server-connection'),
                    str("{'isConnectRequest':true}"))
    pass


def offline_publisher(msg):
    global m5mqtt, mqttSvr
    mqttSvr.publish(str(MQ_TOPIC), msg)


'''
Event Handlers:
1. event_handler():
Adalah fungsi pererekaman suhu pada situasi online. 

2. offline_handler():
Digunakan sebagai event handler saat tidak terdapat koneksi ke internet atau ke server.
'''


def event_handler():
    global label0, label1, label2, label3

    global Record, MQ_SVR
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

    publish_result(Record, MQ_SVR, isNormal)
    wait(2)
    label0.setText(str(""))
    setScreenColor(0xffffff)
    label0 = M5TextBox(60, 0, "    Jarak Ukur",
                       lcd.FONT_DejaVu18, 0x275ea8, rotate=90)
    label1 = M5TextBox(35, 30, " 10-15 cm",
                       lcd.FONT_DejaVu18, 0x275ea8, rotate=90)
    label2 = M5TextBox(50, 20, "",
                       lcd.FONT_DejaVu18, 0x275ea8, rotate=90)


def offline_handler():
    global MAC_ADDR, label0, label1, label2, label3, Record, offline_records, offlineLabel

    Record = record_temp()
    isNormal = check_result(Record)
    label2.setText('' + str(Record) + ' celcius')
    offlineLabel.setText("offline mode-don't turn off ")

    if(isNormal):
        for i in range(2):
            sound_spk(0.5, 440)
            wait(0.175)
    else:
        for i in range(4):
            sound_spk(10, 262)
            wait(0.2)
    ts = "OFFLINE MODE"
    msg = str('{"sensor_mac_addr": "') + str(MAC_ADDR) + str('", "time_stamp":"') + str(ts) + str(
        '", "temperature": ') + str(Record) + str(', "isAlert":') + str(isNormal == False) + str('}')

    offline_index = len(offline_records)
    offline_records[offline_index] = msg
    wait(2)
    label0.setText(str(""))
    setScreenColor(0xffcc33)
    label0 = M5TextBox(60, 0, "    Jarak Ukur",
                       lcd.FONT_DejaVu18, 0x275ea8, rotate=90)
    label1 = M5TextBox(35, 30, " 10-15 cm",
                       lcd.FONT_DejaVu18, 0x275ea8, rotate=90)
    label2 = M5TextBox(50, 20, "",
                       lcd.FONT_DejaVu18, 0x275ea8, rotate=90)
    offlineLabel.setText("offline mode-don't turn off ")


'''
Configuration process:
Bagian ini dijalankan saat memulai proses konfigurasi.
'''
setScreenColor(0x111111)
mqttSvr = M5mqtt('', 'app.itsmyhealth.id', 1882, 'sens1', 'testing1', 300)
label0 = M5TextBox(52, 9, "Text", lcd.FONT_DefaultSmall, 0xFFFFFF, rotate=90)
label1 = M5TextBox(74, 6, "Text1", lcd.FONT_Default, 0xFFFFFF, rotate=90)
label2 = M5TextBox(34, 7, "Text2", lcd.FONT_DefaultSmall, 0xFFFFFF, rotate=90)
label3 = M5TextBox(17, 8, "text3", lcd.FONT_DefaultSmall, 0xFFFFFF, rotate=90)
mqttSvr.subscribe(str('/server-response'), fun__server_response_)
setScreenColor(0x339999)
mqttSvr.start()
configure()

loop_count = 0
# Jika koneksi ke server MQTT belum tersambung loop ini dijalankan untuk memeriksa koneksi.
while not MQTTConnection:
    configure()
    loop_count = (loop_count if isinstance(loop_count, Number) else 0) + 1
    if loop_count > 10:  # Jika pada pemeriksaan kesepuluh koneksi belum terhubung, pemeriksaan dihentikan dan akan memulai offline mode
        break
configure()
wait(1)
setToStart()
wait(1)
# ======== CONFIG END========


'''
Main loop:
Bagian utama proses
'''
counter = 0
while True:
    # main loop yang dijalankan pada mode online
    if(MQTTConnection and wifiCfg.wlan_sta.isconnected()):
        if(check_offline_records() == True):
            # label0 = M5TextBox(60, 0, "Uploading offline records",
            #                    lcd.FONT_DefaultSmall, 0x275ea8, rotate=90)
            # wait(3)
            for i in offline_records.values():
                offline_publisher(i)
            offline_records = {}
        label0.setText(str(""))
        setScreenColor(0xffffff)

        label0 = M5TextBox(60, 0, "    Jarak Ukur",
                           lcd.FONT_DejaVu18, 0x275ea8, rotate=90)
        label1 = M5TextBox(35, 30, " 10-15 cm",
                           lcd.FONT_DejaVu18, 0x275ea8, rotate=90)
        label2 = M5TextBox(50, 20, "",
                           lcd.FONT_DejaVu18, 0x275ea8, rotate=90)
        counter = (counter if isinstance(counter, Number) else 0) + 1
        # start
        # pemanggilan event handler online mode jika button A ditekan
        btnA.wasPressed(event_handler)
        wait(1)
    else:  # main loop yang dijalankan pada offline mode
        # setScreenColor(0xff0000)
        offlineLabel = M5TextBox(
            15, 4, "offline mode-don't turn off ", lcd.FONT_DefaultSmall, 0xda1d1d, rotate=90)
        setScreenColor(0xffcc33)
        label0 = M5TextBox(60, 0, "    Jarak Ukur",
                           lcd.FONT_DejaVu18, 0x275ea8, rotate=90)
        label1 = M5TextBox(35, 30, " 10-15 cm",
                           lcd.FONT_DejaVu18, 0x275ea8, rotate=90)
        label2 = M5TextBox(50, 20, "",
                           lcd.FONT_DejaVu18, 0x275ea8, rotate=90)
        offlineLabel = M5TextBox(
            15, 4, "offline mode-don't turn off ", lcd.FONT_DefaultSmall, 0xda1d1d, rotate=90)
        offlineLabel.setText("offline mode-don't turn off ")

        counter = (counter if isinstance(counter, Number) else 0) + 1
        # event handler offline mode yang dijalankan
        btnA.wasPressed(offline_handler)
        wait(1)
    if counter == 5 and MQTTConnection:  # pada perekaman ke 5, dilakukan pengecekan koneksi server
        MQTTConnection = False
        mqttSvr.publish(str('/sensor/v1/server-connection'),
                        str("{'isConnectRequest':true}"))
        # wifi_status = wifiCfg.wlan_sta.isconnected()
        wait(6)
        counter = 0
    if counter == 5 and not MQTTConnection:
        mqttSvr.publish(str('/sensor/v1/server-connection'),
                        str("{'isConnectRequest':true}"))
        # wifi_status = wifiCfg.wlan_sta.isconnected()
        wait(1)
        counter = 0
