'''

图像识别功能使用前，如果树梅派在开机前有连接的摄像头，
需要先关闭mjpg进程 

请在光照环境稳定且背景为纯色的情况下使用图像识别功能。

'''

import cv2          #导入模块
import numpy as np
import time
import pigpio
import os

#关于色域范围可以百度 HSV
#百科：https://baike.baidu.com/item/HSV/547122?fr=aladdin
#参考：https://blog.csdn.net/leo_888/article/details/88284251


#启动脚本杀死影响程序的进程
os.system('./killmain.sh')

black_lower = np.array([0,0,0])
black_upper = np.array([180,255,46]) #设置黑色区间

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

color_lower = red_lower2    #选择要识别的颜色
color_upper = red_upper2

#方式1：打开mjpg视频流，前提是已经开启了mjpg服务
#stream = "http://127.0.0.1:8080/?action=stream?dummy=param.mjpg"
#cap = cv2.VideoCapture(stream)  #打开摄像头 最大范围 640×480

#方式2：需关闭mjpg服务 ps-elf|rep mjpg   查看摄像头编号 cat /dev/video
cap = cv2.VideoCapture(0)  #打开摄像头 最大范围 640×480

cap.set(3,320)  #设置画面宽度
cap.set(4,240)  #设置画面高度

#类实例化
pi = pigpio.pi()

#引脚定义
PIN_yuntai = 26
PIN_camera = 12
#二维云台初始化位置
pi.set_servo_pulsewidth(PIN_yuntai, 1500)
pi.set_servo_pulsewidth(PIN_camera, 1500)

while 1: #进入无限循环
    #print('time1,{}'.format(time.time()))
    ret,frame = cap.read() #将摄像头拍摄到的画面作为frame的值，ret为布尔值，如果正确读取帧，返回True
    #反转视频镜头
    #frame = cv2.flip(frame, -1)
    
    frame = cv2.GaussianBlur(frame,(5,5),0) #高斯滤波GaussianBlur() 让图片模糊
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV) #将图片的色域转换为HSV的样式 以便检测
    mask = cv2.erode(hsv,None,iterations=2) #显示腐蚀后的图像
    mask = cv2.inRange(mask,color_lower,color_upper)  #设置阈值，去除背景 保留所设置的颜色   
    mask = cv2.GaussianBlur(mask,(3,3),0) #高斯模糊
    res = cv2.bitwise_and(frame,frame,mask=mask) #图像合并
    cnts = cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2] #边缘检测    
    #展现十字架
    #cv2.line(frame, (int(img_w / 2) - 20, int(img_h / 2)), (int(img_w / 2) + 20, int(img_h / 2)), (0, 0, 255), 1)
    #cv2.line(frame, (int(img_w / 2),int(img_h / 2) - 20), (int(img_w / 2), int(img_h / 2) + 20), (0, 0, 255), 1)
      

    if len(cnts) >0 : #通过边缘检测来确定所识别物体的位置信息得到相对坐标
        cnt = max(cnts,key=cv2.contourArea)
        rect = cv2.minAreaRect(cnt)
        # 获取最小外接矩形的4个顶点
        box = cv2.boxPoints(rect)
        
        #绘制轮廓
        cv2.drawContours(frame, [np.int0(box)], -1, (0, 255, 255), 2)
        
        #获取坐标 长宽 角度
        c_x, c_y = rect[0]
        c_h, c_w = rect[1]
        c_angle = rect[2]
                                
        #(x,y),radius = cv2.minEnclosingCircle(cnt)
        #cv2.circle(frame,(int(x),int(y)),int(radius),(255,0,255),2) #画出一个圆
        #if c_h * c_w >= 900 and c_h * c_w <= 1600:
        print(time.time(), 'x=', int(c_x), 'y=', int(c_y), 'c_h=', int(c_h), 'c_w=', int(c_w), 'angle=', int(c_angle))
    
        
    else:
        pass
      
    cv2.imshow('frame',frame) #将具体的测试效果显示出来
    #cv2.imshow('mask',mask)
    #cv2.imshow('res',res)
    if cv2.waitKey(5) & 0xFF == 27: #如果按了ESC就退出 当然也可以自己设置
        break
#使用opencv最后都要这样设置一下
cap.release()  #释放捕获器
cv2.destroyAllWindows() #摧毁所有窗口