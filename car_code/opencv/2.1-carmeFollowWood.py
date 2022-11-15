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
pwm_bias1 = 0   
pwm_value1 = 1500
pwm_bias2 = 0   
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
    
#摄像头跟随
def camera_follow(c_x,c_y):
    global systick_ms_bak,pwm_value1,pwm_value2
    if(int((time.time() * 1000))- systick_ms_bak >= 100):
        systick_ms_bak = int((time.time() * 1000))
        x_bias = c_x - width/2
        y_bias = c_y - hight/2
        if abs(x_bias) < 30 and abs(y_bias) < 30:
            pass
        else: 
            pwm_value1 = pwm_value1 - x_bias
            pwm_value2 = pwm_value2 + y_bias
            pi.set_servo_pulsewidth(PIN_yuntai, pwm_value1)
            pi.set_servo_pulsewidth(PIN_camera, pwm_value2)

#无限循环
while 1: #进入无线循环
    #将摄像头拍摄到的画面作为frame的值
    #print("time1:",time.time())
    ret,frame = cap.read()
    #反转视频镜头
    #frame = cv2.flip(frame, -1)
    #高斯滤波GaussianBlur() 让图片模糊
    frame = cv2.GaussianBlur(frame,(5,5),0)
    #将图片的色域转换为HSV的样式 以便检测
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    #print("time2:",time.time())
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
    #print("time3:",time.time())
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
        #为了防止背景的干扰，限定识别到木块的像素值，木块距摄像头距离20cm左右
        if 30 < c_h < 80 and 30 < c_w < 80:
            #绘制轮廓
            cv2.drawContours(frame, [np.int0(box)], -1, (0, 255, 255), 2)
            
            #print(time.time(), 'x=', int(c_x), 'y=', int(c_y), 'c_h=', int(c_h), 'c_w=', int(c_w), 'angle=', int(c_angle))
            camera_follow(c_x,c_y)
            #print("time4:",time.time())   
            
    #print("time5:",time.time())                                                                                                                   
    cv2.imshow('frame',frame) #将具体的测试效果显示出来
    #print("time6:",time.time())
    #cv2.imshow('mask',mask)
    #cv2.imshow('res',res)
    if cv2.waitKey(5) & 0xFF == 27: #如果按了ESC就退出 当然也可以自己设置
        break

cap.release()
cv2.destroyAllWindows() #后面两句是常规操作,每次使用摄像头都需要这样设置一波

