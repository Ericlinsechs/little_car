'''
图像识别功能使用前，如果树梅派在开机前有连接的摄像头，
需要先关闭mjpg进程 

请在光照环境稳定且背景为纯色的情况下使用图像识别功能。 
'''

import numpy as np #导入库
import cv2
import time
import pigpio
import os

#启动脚本杀死影响程序的进程
os.system('./killmain.sh')

# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades
mouth_cascade = cv2.CascadeClassifier('mouth.xml')
face_cascade = cv2.CascadeClassifier('face.xml')
eye_cascade = cv2.CascadeClassifier('eye.xml')

#获取摄像头数据方式1 从网络获取，相对较慢
#stream = "http://127.0.0.1:8080/?action=stream?dummy=param.mjpg"
#cap = cv2.VideoCapture(stream)

#获取摄像头方式2 数据更快
width = 320
hight = 240

cap = cv2.VideoCapture(0)  #打开摄像头
cap.set(3,width)
cap.set(4,hight)  #设置窗口的大小

#引脚定义
PIN_yuntai = 26
PIN_camera = 12
#全局变量定义
pwm_bias1 = 0   
pwm_value1 = 1500
pwm_bias2 = 0   
pwm_value2 = 1500
systick_ms_bak = 0

#类实例化
pi = pigpio.pi()

pi.set_servo_pulsewidth(PIN_yuntai, pwm_value1)
pi.set_servo_pulsewidth(PIN_camera, pwm_value2-200)

#摄像头跟随
def camera_follow(x,y):
    global systick_ms_bak,pwm_value1,pwm_value2
    x_bias = x - width/2
    y_bias = y - hight/2
    #print(int(x_bias),int(y_bias))
    if abs(x_bias) < 30 and abs(y_bias) < 30:
        pass
    else: 
        pwm_value1 = pwm_value1 - x_bias//3
        pwm_value2 = pwm_value2 + y_bias//3
        pi.set_servo_pulsewidth(PIN_yuntai, pwm_value1)
        pi.set_servo_pulsewidth(PIN_camera, pwm_value2)
     

while True:
    ret, img = cap.read()
    #img = cv2.flip(img, -1)#反转视频镜头
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray,1.1,5)
    findOk = 0
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        
        x = int(x+w/2)
        y = int(y+h/2)
        
        findOk = 1
   
    if findOk == 1:
        print ('time:',time.time(), ' x=',x, ' y=',y)
        camera_follow(x,y)

        #检测眼睛
        #eyes = eye_cascade.detectMultiScale(roi_gray)
        #for (ex,ey,ew,eh) in eyes:
            #cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
        
        #检测嘴巴
        #mouth = mouth_cascade.detectMultiScale(roi_gray)
        #for (ex,ey,ew,eh) in mouth:
            #cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,0,255),2)

    cv2.imshow('video',img)

    k = cv2.waitKey(30) & 0xff
    if k == 27: # press 'ESC' to quit
        break

cap.release()
cv2.destroyAllWindows()
