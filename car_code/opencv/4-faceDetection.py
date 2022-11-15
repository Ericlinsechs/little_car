'''
图像识别功能使用前，如果树梅派在开机前有连接的摄像头，
需要先关闭mjpg进程

请在光照环境稳定且背景为纯色的情况下使用图像识别功能。 
'''

import numpy as np  #导入库
import cv2
import time
import pigpio
import os

#启动脚本杀死影响程序的进程
os.system('./killmain.sh')

# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades
face_cascade = cv2.CascadeClassifier('face.xml')
mouth_cascade = cv2.CascadeClassifier('mouth.xml')
eye_cascade = cv2.CascadeClassifier('eye.xml')

#引脚定义
PIN_yuntai = 26
PIN_camera = 12
#全局变量定义   
pwm_value1 = 1500 
pwm_value2 = 1500
#类实例化
pi = pigpio.pi()

pi.set_servo_pulsewidth(PIN_yuntai, pwm_value1)
pi.set_servo_pulsewidth(PIN_camera, pwm_value2-200)  #根据自己的情况调整摄像头的角度


#获取摄像头数据方式1 从网络获取，相对较慢
#stream = "http://127.0.0.1:8080/?action=stream?dummy=param.mjpg"
#cap = cv2.VideoCapture(stream)

#获取摄像头方式2 数据更快
cap = cv2.VideoCapture(0) #连接摄像头的对象 0表示摄像头的编号

#缩小显示比例
cap.set(3,320) # set Width
cap.set(4,240) # set Height

while True:
    ret, img = cap.read()
    #ret, img = cap.read()中，cap.read()是按帧读取，其会返回两个值：ret,img（ret是布尔值，
    #如果读取帧是正确的则返回True，如果文件读取到结尾，它的返回值就为False；后面的img该帧图像的三维矩阵BGR形式。)
    #img = cv2.flip(img, -1)#反转视频镜头
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #处理图像转灰度
    faces = face_cascade.detectMultiScale(gray,1.1,5) ## 检测人脸 返回列表 每个元素都是(x, y, w, h)表示矩形的左上角和宽高

    for (x,y,w,h) in faces: # 画出人脸的矩形
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2) # 画矩形 在img图片上画， 传入左上角和右下角坐标 矩形颜色 和线条宽度
        roi_gray = gray[y:y+h, x:x+w]  # 把脸单独拿出来
        roi_color = img[y:y+h, x:x+w]  
        
        x = int(x+w/2)
        y = int(y+h/2) 
        
        print (x, y)
        #检测眼睛
        eyes = eye_cascade.detectMultiScale(roi_gray)  #在脸上检测眼睛   
        for (ex,ey,ew,eh) in eyes:  #把眼睛画出来
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
        
        #检测嘴巴
        mouth = mouth_cascade.detectMultiScale(roi_gray)
        for (ex,ey,ew,eh) in mouth:
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,0,255),2)

    cv2.imshow('video',img)

    k = cv2.waitKey(30) & 0xff
    if k == 27: # press 'ESC' to quit
        break

cap.release()
cv2.destroyAllWindows()
