'''
 图像识别功能使用前，如果树梅派在开机前有连接的摄像头，
需要先关闭mjpg进程 

请在光照环境稳定且背景为纯色的情况下使用图像识别功能。 
'''

import cv2                 #导入库
import numpy as np 
import time
import z_uart as myUart
import pigpio
import os

#启动脚本杀死影响程序的进程
os.system('./killmain.sh')

#引脚定义
PIN_yuntai = 26
PIN_camera = 12

cap = cv2.VideoCapture(0)  #打开摄像头
cap.set(3,160)
cap.set(4,120)             #设置窗口的大小
#类实列化
pi = pigpio.pi()
#初始化二维云台
pi.set_servo_pulsewidth(PIN_yuntai, 1500)
pi.set_servo_pulsewidth(PIN_camera, 2300)

#全局变量
systick_ms_bak = 0

myUart.setup_uart(115200)

def Tracing(cx, cy):
    global systick_ms_bak
    if(int((time.time() * 1000))- systick_ms_bak > 100):
        systick_ms_bak = int((time.time() * 1000))
        if cx<=60:
            left_speed = 0
            right_speed = 450
            car_run(left_speed,right_speed,left_speed,right_speed)
        elif cx>60 and cx<120:
            left_speed = 300 #- x*10
            right_speed = 300 #+ x*10
            car_run(left_speed,right_speed,left_speed,right_speed)

        elif cx>=120:
            left_speed = 450
            right_speed = 0
            car_run(left_speed,right_speed,left_speed,right_speed)

def car_run(l1,l2,l3,l4):
    testStr = "{#006P%04dT0000!#007P%04dT0000!#008P%04dT0000!#009P%04dT0000!}" % (1500+l1,1500-l2,1500+l3,1500-l4,)
    print(testStr)
    myUart.uart_send_str(testStr)

while True: #进入无线循环    
    # Capture the frames
    ret, frame = cap.read()  #ret, img = cap.read()中，cap.read()是按帧读取，其会返回两个值：ret,img（ret是布尔值，
                             #如果读取帧是正确的则返回True，如果文件读取到结尾，它的返回值就为False；后面的frame该帧图像的三维矩阵BGR形式。)
    
    #反转视频镜头
    #frame = cv2.flip(frame, -1)
    
    # Crop the image
    crop_img =frame[60:120, 0:160] #frame是相对于父视图的坐标系来定位的。如果你这样设置frame:(0,0,100,200),也就是在父视图左上角添加了一个宽100，
                                   #高200的子视图（前提是没有改变父视图的bounds，接下来会有介绍bounds）。
    # 转化成BGR样式
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    #高斯滤波GaussianBlur() 让图片模糊
    blur = cv2.GaussianBlur(gray,(5,5),0)
    #二值化
    ret,thresh1 = cv2.threshold(blur,60,255,cv2.THRESH_BINARY_INV)
    #腐蚀，去除图像毛次，减少细微影响
    mask = cv2.erode(thresh1, None, iterations=2)
    #膨胀，
    mask = cv2.dilate(mask, None, iterations=2)
    
    # 查找轮廓
    image,contours,hierarchy = cv2.findContours(mask.copy(), 1, cv2.CHAIN_APPROX_NONE)
    # Find the biggest contour (if detected)
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        #根据得到的坐标画出蓝线，方便看出偏差
        cv2.line(crop_img,(cx,0),(cx,720),(255,0,0),1)
        cv2.line(crop_img,(0,cy),(1280,cy),(255,0,0),1)
        #绘制绿色轮廓
        cv2.drawContours(crop_img, contours, -1, (0,255,0), 1)
        
        #print(time.time(), int(cx),int(cy))
        Tracing(cx, cy)
        
    else:
        print("I don't see the line" )
    
    
    cv2.imshow('frame',crop_img) #将具体的测试效果显示出来
    #cv2.imshow('mask',mask)
    #cv2.imshow('res',res)
    if cv2.waitKey(5) & 0xFF == 27: #如果按了ESC就退出 当然也可以自己设置
        myUart.uart_send_str("#255P1500T0000!")
        break

cap.release()
cv2.destroyAllWindows() #后面两句是常规操作,每次使用摄像头都需要这样设置一波