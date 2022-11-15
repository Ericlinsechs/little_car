# -*- coding:utf-8 -*-
#导入模块
import time
import re
import RPi.GPIO as GPIO
from rpi_ws281x import Adafruit_NeoPixel, Color
import threading
import pigpio

import z_key as myKey
import z_led as myLed
import z_beep as myBeep
import z_uart as myUart
import z_lirc as myLirc
import z_socket as mySocket

#端口模式设置
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# LED 配置:
LED_COUNT      = 9      # 要控制LED的数量.
LED_PIN        = 18      # GPIO接口 (PWM编码).
LED_BRIGHTNESS = 255    # 设置LED亮度 (0-255)
#以下LED配置无需修改
LED_FREQ_HZ    = 800000  # LED信号频率（以赫兹为单位）（通常为800khz）
LED_DMA        = 10       # 用于生成信号的DMA通道（尝试10）
LED_INVERT     = False   # 反转信号（使用NPN晶体管电平移位时）
#引脚定义
PIN_yuntai = 26
PIN_camera = 12

#引脚定义
PIN_lirc = 27

#超声波引脚定义
TRIG = 23
ECHO = 22

#pigpio实例化
pi = pigpio.pi()

#全局变量定义
systick_ms_bak = 0
systick_ms_group_bak = 0
systick_ms_bak_rgb = 0
car_mode = 0
car_mode_bak = 0
pwm_value1 = 1500
pwm_value2 = 1500
dis = 100
lirc_value = 0

#大循环LED灯
def loop_led():
    global systick_ms_bak
    if(int((time.time() * 1000))- systick_ms_bak > 500):
        systick_ms_bak = int((time.time() * 1000))
        myLed.flip()
#按键   
def loop_key():
    global key1_flag, key2_flag
    if(myKey.key1() == 0):
        time.sleep(0.02)
        if(myKey.key1() == 0):
            beep_on_once()
            while myKey.key1() == 0:
                pass
            
    if(myKey.key2() == 0):
        time.sleep(0.02)
        if(myKey.key2() == 0):
            beep_on_once()
            while myKey.key2() == 0:
                pass

#串口检测
def loop_uart():
    if myUart.uart_get_ok == 2:
        print(myUart.uart_receive_buf)
        parse_cmd(myUart.uart_receive_buf)
        myUart.uart_receive_buf = ''
        myUart.uart_get_ok = 0
    elif myUart.uart_get_ok == 1 or myUart.uart_get_ok == 3:
        print(myUart.uart_receive_buf)
        myUart.uart_send_str(myUart.uart_receive_buf)
        myUart.uart_receive_buf = ''
        myUart.uart_get_ok = 0
#网络连接服务
def loop_socket():
    if mySocket.socket_get_ok:
       myUart.uart_get_ok =  mySocket.socket_get_ok
       myUart.uart_receive_buf = mySocket.socket_receive_buf
       mySocket.socket_receive_buf = ''
       mySocket.socket_get_ok = 0
#指令解析       
def parse_cmd(myStr):
    global car_mode,car_mode_bak,voice_flag,voice_mode
    if myStr.find('$VOICE!') >= 0:
        pass       
    elif myStr.find('$QJ!') >= 0:
        car_mode = 1
        beep_on_once()
    elif myStr.find('$HT!') >= 0:
        car_mode = 2        
        beep_on_once()
    elif myStr.find('$ZZ!') >= 0:
        car_mode = 3
        beep_on_once()
    elif myStr.find('$YZ!') >= 0:
        car_mode = 4
        beep_on_once()
    elif myStr.find('$ZPY!') >= 0:
        car_mode = 5
        beep_on_once()
    elif myStr.find('$YPY!') >= 0:
        car_mode = 6
        beep_on_once()
    elif myStr.find('$ZYBZ!') >= 0:
        car_mode = 7
        beep_on_once()
    elif myStr.find('$WTGS!') >= 0:
        car_mode = 8
        beep_on_once()
    elif myStr.find('$TZ!') >= 0:
        car_mode = 0
        beep_on_once()
    elif myStr.find('$CUP!') >= 0:
        car_mode = 9
        beep_on_once()
    elif myStr.find('$CDOWN') >= 0:
        car_mode = 10
        beep_on_once()
    elif myStr.find('$CLEFT') >= 0:
        car_mode = 11
        beep_on_once()
    elif myStr.find('$CRIGHT') >= 0:
        car_mode = 12
        beep_on_once()
    elif myStr.find('$QJ1') >= 0:
        beep_on_once()
        myUart.uart_send_str("#006P2500T1000!#007P0500T1000!#008P2500T1000!#009P0500T1000!")
    elif myStr.find('$HT1') >= 0:
        beep_on_once()
        myUart.uart_send_str("#006P0500T1000!#007P2500T1000!#008P0500T1000!#009P2500T1000!")
    elif myStr.find('$ZZ1') >= 0:
        beep_on_once()
        myUart.uart_send_str("#006P0500T1000!#007P0500T1000!#008P0500T1000!#009P0500T1000!")
    elif myStr.find('$YZ1') >= 0:
        beep_on_once()
        myUart.uart_send_str("#006P2500T1000!#007P2500T1000!#008P2500T1000!#009P2500T1000!")
    
def loop_lirc():
    global lirc_value,car_mode,systick_ms_bak,car_mode_bak
    if lirc_value > 0:
        myBeep.beep(0.1)
        if lirc_value == 1:
            car_mode = 0
        elif lirc_value == 5:
            car_mode = 1
        elif lirc_value == 11:
            car_mode = 2
        elif lirc_value == 7:
            car_mode = 3
        elif lirc_value == 9:
            car_mode = 4
        elif lirc_value == 8:
            car_stop()
        elif lirc_value == 13:
            car_mode = 7
        elif lirc_value == 14:
            car_mode = 8
        lirc_value = 0
                          
def loop_car_mode():
    global car_mode,car_mode_bak
    if car_mode_bak != car_mode:
        car_mode_bak = car_mode
        if car_mode == 0:
            myUart.uart_send_str("#012P1515T1000!")
            car_stop()
            #rgb_show(0)
        elif car_mode == 1:
            myUart.uart_send_str("#012P1511T1000!")
            car_go_back(800)
        elif car_mode == 2:
            myUart.uart_send_str("#012P1512T1000!")
            car_go_back(-800)
        elif car_mode == 3:
            myUart.uart_send_str("#012P1513T1000!")
            car_left_turn(-800)            
        elif car_mode == 4:
            myUart.uart_send_str("#012P1514T1000!")
            car_right_turn(800)
        elif car_mode == 5:
            car_left_right_run(-800)
        elif car_mode == 6:
            car_left_right_run(800)                      
        
    if car_mode == 7:
        car_zybz()
    elif car_mode == 8:
        car_wtgs()
    elif car_mode == 9:
        camera_up_down(-500)
    elif car_mode == 10:
        camera_up_down(500)
    elif car_mode == 11:
        camera_l_r(500)
    elif car_mode == 12:
        camera_l_r(-500)  
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
             #print("Get the key: 0x%02x" %data[2])
             parse_code(data[2])
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

#初始化开启示意
def setup_start():
    beep_on_once()
    beep_on_once()
    beep_on_once()

def setup_lirc():
    GPIO.setup(PIN_lirc,GPIO.IN,GPIO.PUD_UP)

#初始化超声波    
def setup_csb():
    GPIO.setup(TRIG, GPIO.OUT,initial = 0)
    GPIO.setup(ECHO, GPIO.IN,pull_up_down = GPIO.PUD_UP)

def setup_show():
    
    rgb_show(1)
    time.sleep(1)
    rgb_show(2)
    time.sleep(1)
    rgb_show(3)
    time.sleep(1)   
    rgb_show(0)
    


#超声波测距    
def distance():
    GPIO.output(TRIG, 0)
    time.sleep(0.000002)

    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)
   
    while GPIO.input(ECHO) == 0:
        a = 0
    time1 = time.time()
    while GPIO.input(ECHO) == 1:
        a = 1
    time2 = time.time()

    during = time2 - time1
    return during * 340 / 2 * 100

#自由避障
def car_zybz():
    global systick_ms_bak
    if(int((time.time() * 1000))- systick_ms_bak > 50):
        systick_ms_bak = int((time.time() * 1000))
        dis = distance()
        if int(dis) >= 100:
            #rgb_show(3)
            car_go_back(800)
        elif 50 <= int(dis) < 100:
            #rgb_show(1)
            #rgb_show(3)
            car_go_back(600)
        elif 30 <= int(dis) < 50:
            #rgb_show(2)
            car_go_back(400)
        else:
            #rgb_show(1)
            car_right_turn(500)

#物体跟随
def car_wtgs():
    global systick_ms_bak
    if(int((time.time() * 1000))- systick_ms_bak > 50):
        systick_ms_bak = int((time.time() * 1000))
        print(time.time())
        dis = distance()
        if int(dis) > 60 or 20 < int(dis) < 40:
            car_stop()
        elif 40 <= int(dis) <= 60:
            car_go_back(600)
        elif int(dis) <= 20:
            car_go_back(-600)

#控制RGB灯亮起
def rgb_show(x):
    if x == 0:
        for i in range(0,strip.numPixels()):  
            strip.setPixelColor(i, Color(0,0,0))
            strip.show()
    elif x == 1:
        for i in range(0,strip.numPixels()):  
            strip.setPixelColor(i, Color(255,0,0))
            strip.show()
    elif x == 2:
        for i in range(0,strip.numPixels()):  
            strip.setPixelColor(i, Color(0,255,0))
            strip.show()
    elif x == 3:
        for i in range(0,strip.numPixels()):  
            strip.setPixelColor(i, Color(0,0,255))
            strip.show()
  
#蜂鸣器
def beep_on_once():
    myBeep.on()
    time.sleep(0.1)
    myBeep.off()
    time.sleep(0.1)  

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
   
#摄像头上下转动    
def camera_up_down(speed):
    global systick_ms_bak,pwm_value2
    if(int((time.time() * 1000))- systick_ms_bak > 20):
        systick_ms_bak = int((time.time() * 1000))
        pi.set_servo_pulsewidth(PIN_camera, pwm_value2)
        pwm_value2 = pwm_value2 +speed//100
        if pwm_value2 > 2500:
            pwm_value2 = 2500
        if pwm_value2 < 500:
            pwm_value2 = 500
        print(pwm_value2)
        return
#摄像头左右转动    
def camera_l_r(speed):
    global systick_ms_bak,pwm_value1
    if(int((time.time() * 1000))- systick_ms_bak > 20):
        systick_ms_bak = int((time.time() * 1000))        
        pi.set_servo_pulsewidth(PIN_yuntai, pwm_value1)
        pwm_value1 = pwm_value1 + speed//100
        if pwm_value1 > 2500:
            pwm_value1 = 2500
        if pwm_value1 < 500:
            pwm_value1 = 500
        print(pwm_value1)
        return 
            
#释放IO资源
def destory():
    myLed.off()
    myBeep.off()
    GPIO.cleanup()
  

#大循环
if __name__ == '__main__':
    time.sleep(5)
    myLed.setup_led()        #led初始化
    myBeep.setup_beep()      #蜂鸣器初始化
    setup_csb()              #初始化超声波
    setup_lirc()             #初始化红外
    myKey.setup_key()        #按键初始化
        
    setup_start()            #启动示意滴滴滴三声
    
    myUart.setup_uart(115200) #设置串口
    
    mySocket.setup_socket(1314)
    #创建NeoPixel对象
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
    #初始化库
    strip.begin()
    setup_show()
    #二维云台初始化
    pi.set_servo_pulsewidth(PIN_camera, 1500)
    pi.set_servo_pulsewidth(PIN_yuntai, 1500)
   
    try:
        while True:            
            loop_led()
            loop_key()
            loop_uart()
            loop_socket()
            lircEvent()
            loop_lirc()
            loop_car_mode()
    except KeyboardInterrupt:
        destory()
        