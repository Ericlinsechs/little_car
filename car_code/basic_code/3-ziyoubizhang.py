#导入模块
import time
import RPi.GPIO as GPIO

import z_uart as myUart

#端口模式设置
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#引脚定义
BEEP_PIN = 21
LED_PIN = 4
KEY1_PIN = 24
KEY2_PIN = 25

#超声波引脚定义
TRIG = 23
ECHO = 22

#全局变量定义
systick_ms_bak = 0
dis = 100
#初始化IO口
def setup_gpio():
    GPIO.setup(LED_PIN, GPIO.OUT,initial = 1)     
    GPIO.setup(BEEP_PIN, GPIO.OUT, initial = 0)   
    GPIO.setup(KEY1_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)  
    GPIO.setup(KEY2_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#初始化超声波    
def setup_csb():
    GPIO.setup(TRIG, GPIO.OUT,initial = 0)
    GPIO.setup(ECHO, GPIO.IN,pull_up_down = GPIO.PUD_UP)
    
#大循环LED灯
def loop_led():
    global systick_ms_bak
    if(int((time.time() * 1000))- systick_ms_bak > 500):
        systick_ms_bak = int((time.time() * 1000))
        GPIO.output(LED_PIN, not GPIO.input(LED_PIN))  #led引脚电平翻转
#间接发出响声，x代表间接的时间，单位为秒
def beep(x):
    GPIO.output(BEEP_PIN,1)  #蜂鸣器鸣叫
    time.sleep(x)
    GPIO.output(BEEP_PIN,0)  #蜂鸣器关闭
    time.sleep(x)
#启动示意
def setup_start():
    for i in range(3):
        beep(0.1)

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
def car_move():
    global systick_ms_bak
    if(int((time.time() * 1000))- systick_ms_bak > 100):
        systick_ms_bak = int((time.time() * 1000))
        dis = distance()
        if int(dis) >= 100:
            car_go_back(800)
        elif 50 <= int(dis) < 100:
            car_go_back(600)
        elif 20 <= int(dis) < 50:
            car_go_back(400)
        else:
            car_right_turn(500)

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
#大循环
if __name__ == '__main__':
    
    setup_gpio()             #初始化IO口
    setup_start()            #初始化示意蜂鸣器滴滴滴三声
    setup_csb()              #初始化超声波
    myUart.setup_uart(115200) #设置串口
     
    try:
        while True:
            loop_led()
            car_move()
    except KeyboardInterrupt:
        destory() 
    
    
    