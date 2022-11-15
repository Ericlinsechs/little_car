#导包
import RPi.GPIO as GPIO
import time
import threading


#引脚定义
PIN_lirc = 27
BEEP_PIN = 21

#解析存放变量
lirc_value = 0

#端口模式设置
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def setup_beep():
    GPIO.setup(BEEP_PIN, GPIO.OUT, initial = 0)
    
def beep():
    GPIO.output(BEEP_PIN, 1)
    time.sleep(0.1)
    GPIO.output(BEEP_PIN, 0)
    time.sleep(0.1)
    
#数据解析
def parse_code(key_val):
    global lirc_value
    if(key_val==0x45):
        print("Button POWER")
        lirc_value = 1
    elif(key_val==0x46):
        print("Button MENU")
        lirc_value = 2
    elif(key_val==0x47):
        print("Button VOICE")
        lirc_value = 3
    elif(key_val==0x44):
        print("Button MODE")
        lirc_value = 4
    elif(key_val==0x40):
        print("Button +")
        lirc_value = 5
    elif(key_val==0x43):
        print("Button BACK")
        lirc_value = 6
    elif(key_val==0x07):
        print("Button PREV")
        lirc_value = 7
    elif(key_val==0x15):
        print("Button PLAY/STOP")
        lirc_value = 8
    elif(key_val==0x09):
        print("Button NEXT")
        lirc_value = 9
    elif(key_val==0x16):
        print("Button 0")
        lirc_value = 10
    elif(key_val==0x19):
        print("Button -")
        lirc_value = 11
    elif(key_val==0x0d):
        print("Button OK")
        lirc_value = 12
    elif(key_val==0x0c):
        print("Button 1")
        lirc_value = 13
    elif(key_val==0x18):
        print("Button 2")
        lirc_value = 14
    elif(key_val==0x5e):
        print("Button 3")
        lirc_value = 15
    elif(key_val==0x08):
        print("Button 4")
        lirc_value = 16
    elif(key_val==0x1c):
        print("Button 5")
        lirc_value = 17
    elif(key_val==0x5a):
        print("Button 6")
        lirc_value = 18
    elif(key_val==0x42):
        print("Button 7")
        lirc_value = 19
    elif(key_val==0x52):
        print("Button 8")
        lirc_value = 20
    elif(key_val==0x4a):
        print("Button 9")
        lirc_value = 21


def lircEvent():

    if GPIO.input(PIN_lirc) == 0:
        count = 0
        while GPIO.input(PIN_lirc) == 0 and count < 200:
            count += 1
            time.sleep(0.00006)

        count = 0
        while GPIO.input(PIN_lirc) == 1 and count < 80:
            count += 1
            time.sleep(0.00006)

        idx = 0
        cnt = 0
        data = [0,0,0,0]
        for i in range(0,32):
            count = 0
            while GPIO.input(PIN_lirc) == 0 and count < 15:
                count += 1
                time.sleep(0.00006)

            count = 0
            while GPIO.input(PIN_lirc) == 1 and count < 40:
                count += 1
                time.sleep(0.00006)

            if count > 8:
                data[idx] |= 1<<cnt
            if cnt == 7:
                cnt = 0
                idx += 1
            else:
                cnt += 1
        if data[0]+data[1] == 0xFF and data[2]+data[3] == 0xFF:
             print("Get the key: 0x%02x" %data[2])
             parse_code(data[2])

             

def setup_lirc():
    #端口模式设置
    GPIO.setup(PIN_lirc,GPIO.IN,GPIO.PUD_UP)
    


def loop_lirc():
    global lirc_value
    if lirc_value > 0:
        beep()
        lirc_value = 0

if __name__ == '__main__':
    setup_beep()
    #发出哔哔哔作为开机声音
    beep()
    beep()
    beep()
    setup_lirc()
    print("Lirc test start...")
    
    try:
        while True:
            lircEvent()
            loop_lirc()
    except KeyboardInterrupt:
        GPIO.cleanup();

