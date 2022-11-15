#导包
import RPi.GPIO as GPIO
import time
import threading

import z_beep as myBeep
import z_uart as myUart
#引脚定义
PIN_lirc = 27

#解析存放变量
lirc_value = 0
systick_ms_bak = 0
next_time = 20
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
    return lirc_value

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

'''
函数功能：串口发送指令控制电机转动
范围：-1000～+1000
'''
def car_run(speed_l1,speed_r1,speed_l2,speed_r2):
    #global speed_l1,speed_r1,speed_l2,speed_r2 
    textSrt = '#006P{:0>4d}T0000!#007P{:0>4d}T0000!#008P{:0>4d}T0000!#009P{:0>4d}T0000!'.format(speed_l1,speed_r1,speed_l2,speed_r2)
    print(textSrt)
    myUart.uart_send_str(textSrt)

'''
函数功能：小车前进后退
正值小车前进，负值小车后退
范围：-1000～+1000
'''
def car_go_back(speed):
    car_run(1500+speed,1500-speed,1500+speed,1500-speed)

'''
函数功能：小车左转
负值小车左转
范围：0～+1000
'''
def car_left_turn(speed):
    speedl = 1500+speed*2//3
    speedr = 1500+speed
    car_run(speedl,speedr,speedl,speedr)

'''
函数功能：小车右转
正值小车右转
范围：-1000～0
'''
def car_right_turn(speed):
    speedl = 1500+speed
    speedr = 1500+speed*2//3
    car_run(speedl,speedr,speedl,speedr)

'''
函数功能：小车左右平移
负值小车左转，正值右转
范围：-1000～+1000
'''
def car_left_right_run(speed):
    speed1 = 1500+speed
    speed2 = 1500-speed
    car_run(speed1,speed1,speed2,speed2)
'''
函数功能：小车停止
'''
def car_stop():
    myUart.uart_send_str('#255P1500T1000!')
#关闭    
def destory():
    GPIO.output(LED_PIN, 1)
    GPIO.output(BEEP_PIN, 0)
    GPIO.cleanup()
    car_stop()
        

def setup_lirc():
    #端口模式设置
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_lirc,GPIO.IN,GPIO.PUD_UP)
  
def loop_lirc():
    global lirc_value
    if lirc_value > 0:
        myBeep.beep(0.1)
        #print(lirc_value)
        if lirc_value == 1:
            car_stop()
        elif lirc_value == 5:
            car_go_back(800)
            time.sleep(3)
        elif lirc_value == 11:
            car_go_back(-800)
            time.sleep(3)
        elif lirc_value == 7:
            car_left_turn(-800)
            time.sleep(3)
        elif lirc_value == 9:
            car_right_turn(800)
            time.sleep(3)
        elif lirc_value == 8:
            car_stop()        
        lirc_value = 0
    else:
        car_stop()
        
if __name__ == '__main__':
    myBeep.setup_beep()
    #发出哔哔哔作为开机声音
    myBeep.beep(0.1)
    myBeep.beep(0.1)
    myBeep.beep(0.1)
    myUart.setup_uart(115200) #设置串口
    setup_lirc()    
    print("Lirc test start...")    
    try:
        while True:
            lircEvent()
            loop_lirc()           
    except KeyboardInterrupt:
        GPIO.cleanup()

