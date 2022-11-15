'''

图像识别功能使用前，如果树梅派在开机前有连接的摄像头，
需要先关闭mjpg进程 

请在光照环境稳定且背景为纯色的情况下使用图像识别功能。

'''

import cv2   #导入库
import numpy as np
import time
import threading
import pigpio
import os

import z_uart as myUart
import z_beep as myBeep
from math import *

#启动脚本杀死影响程序的进程
os.system('./killmain.sh')

#关于色域范围可以百度 HSV
#百科：https://baike.baidu.com/item/HSV/547122?fr=aladdin
#参考：https://blog.csdn.net/leo_888/article/details/88284251
red_lower1 = np.array([0,43,46])
red_upper1 = np.array([10,255,255]) #设置红色区间1

red_lower2 = np.array([156,43,46])
red_upper2 = np.array([180,255,255]) #设置红色区间2

green_lower = np.array([37,43,46])
green_upper = np.array([77,255,255]) #设置绿色区间

blue_lower = np.array([100,43,46])
blue_upper = np.array([124,255,255]) #设置蓝色区间

text_lower = np.array([0,0,30])
text_upper = np.array([200,43,70]) #设置test区间

color_lower = blue_lower    #选择要识别的颜色
color_upper = blue_upper

#引脚定义
PIN_yuntai = 26
PIN_camera = 12
#全局变量定义
c_x = 160
c_y = 120
x_bias = 0
y_bias = 0
area = 0
next_time = 50  
pwm_value1 = 1500   
pwm_value2 = 1500

systick_ms_bak = 0
#使用之前,如果连接了摄像头，需要先关闭mjpg进程 ps -elf|grep mjpg  找到进程号，杀死进程  sudo kill -9 xxx   xxx代表进程号

#类实例化
pi = pigpio.pi()

width = 320
hight = 240

cap = cv2.VideoCapture(0)  #打开摄像头 最大范围 640×480
cap.set(3,width)  #设置画面宽度
cap.set(4,hight)  #设置画面高度

myBeep.setup_beep()
myUart.setup_uart(115200)

#发出哔哔哔作为开机声音
myBeep.beep(0.1)
myBeep.beep(0.1)
myBeep.beep(0.1)

pi.set_servo_pulsewidth(PIN_yuntai, pwm_value1)
pi.set_servo_pulsewidth(PIN_camera, pwm_value2)

#小车跟随
def car_follow():
    global systick_ms_bak,next_time,x_bias,y_bias,area
    while True:
        if int((time.time() * 1000))- systick_ms_bak >= int(next_time):
            systick_ms_bak = int((time.time() * 1000))            
            #print(int(x_bias),int(y_bias),int(area))   
            if abs(x_bias) < 50 and abs(y_bias) < 50:
                car_stop()
                next_time = 50
            elif int(x_bias) > 50:
                next_time = 0
                interval_time = x_bias/100
                car_right_turn(800)
                time.sleep(interval_time/1000)
                car_stop()
            elif int(x_bias) < -50:
                next_time = 0
                interval_time = -x_bias/100
                car_left_turn(-800)
                time.sleep(interval_time/1000)
                car_stop()
            #通过判断轮廓的面积来判断木块的远近，
            if 6400 < area < 10000:
                car_stop()
                next_time = 50
            elif area >= 10000:
                next_time = 50
                car_go_back(-500)
            elif 400 < area < 1000:
                next_time = 50
                car_go_back(500)
        
                                                  
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

C = threading.Thread(target=car_follow)
C.setDaemon(True)
C.start()

#无限循环
while 1: #进入无线循环
    #将摄像头拍摄到的画面作为frame的值
    ret,frame = cap.read()
    #反转视频镜头
    #frame = cv2.flip(frame, -1)
    #高斯滤波GaussianBlur() 让图片模糊
    frame = cv2.GaussianBlur(frame,(5,5),0)
    #将图片的色域转换为HSV的样式 以便检测
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV) 
    #遍历颜色字典
    #for i in color_dist:
    #设置阈值，去除背景 保留所设置的颜色
    #mask = cv2.inRange(hsv, color_dist[i]['Lower'], color_dist[i]['Upper'])
    mask = cv2.inRange(hsv,color_lower,color_upper)  #设置阈值，去除背景 保留所设置的颜色
    #显示腐蚀后的图像
    mask = cv2.erode(mask,None,iterations=2)
    
    #高斯模糊
    mask = cv2.GaussianBlur(mask,(3,3),0)
    
    #图像合并
    res = cv2.bitwise_and(frame,frame,mask=mask) 

    #边缘检测
    cnts = cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2] 
    x_bias = 0
    y_bias = 0
    area = 0
    if len(cnts) >0 : #通过边缘检测来确定所识别物体的位置信息得到相对坐标

        cnt = max(cnts,key=cv2.contourArea)
        rect = cv2.minAreaRect(cnt)
        # 获取最小外接矩形的4个顶点
        box = cv2.boxPoints(rect)
                    
        #获取坐标 长宽 角度
        c_x, c_y = rect[0]
        c_h, c_w = rect[1]
        c_angle = rect[2]
        if c_angle<-45:
            c_angle = -(90+c_angle)
        #为了防止背景的干扰，限定识别到木块的像素值范围
        if 20 < c_h < 150 and 20 < c_w < 150:
            #绘制轮廓
            cv2.drawContours(frame, [np.int0(box)], -1, (0, 255, 255), 2)
            x_bias = c_x - width/2
            y_bias = c_y - hight/2
            area = c_h*c_w
            #print(time.time(), 'x=', int(c_x), 'y=', int(c_y), 'c_h=', int(c_h), 'c_w=', int(c_w), 'angle=', int(c_angle))
    cv2.imshow('frame',frame) #将具体的测试效果显示出来
    #cv2.imshow('mask',mask)
    #cv2.imshow('res',res)
    if cv2.waitKey(5) & 0xFF == 27: #如果按了ESC就退出 当然也可以自己设置
        break




cap.release()
cv2.destroyAllWindows() #后面两句是常规操作,每次使用摄像头都需要这样设置一波

