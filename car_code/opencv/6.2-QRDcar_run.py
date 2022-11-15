'''
图像识别功能使用前，如果树梅派在开机前有连接的摄像头，
需要先关闭mjpg进程 

请在光照环境稳定且背景为纯色的情况下使用图像识别功能。
'''
import cv2  #导入库
import time
import pyzbar.pyzbar as pyzbar
import pigpio
import threading
import os

import z_uart as myUart
import z_beep as myBeep
from math import *

#启动脚本杀死影响程序的进程
os.system('./killmain.sh')

#引脚定义
PIN_yuntai = 26
PIN_camera = 12
#全局变量定义
mode  = 0
systick_ms_bak = 0
next_time = 0
barcodeData = ''
data = ''
#定义二维码内容
go = 'go'
back = 'back'
leftturn = 'leftturn' 
rightturn = 'rightturn'
leftrun = 'leftrun'
rightrun = 'rightrun'
stop = 'stop'

#类实例化
pi = pigpio.pi()
        
myBeep.setup_beep()
myUart.setup_uart(115200)

#发出哔哔哔作为开机声音
myBeep.beep(0.1)
myBeep.beep(0.1)
myBeep.beep(0.1)

pi.set_servo_pulsewidth(PIN_yuntai, 1500)
pi.set_servo_pulsewidth(PIN_camera, 1500)

def car_move():
    global systick_ms_bak,data,barcodeData,next_time,mode
    if(int((time.time() * 1000))- systick_ms_bak > next_time):
        systick_ms_bak = int((time.time() * 1000))
        
        if int(next_time) == 1000:
            next_time = 0
            mode = 0
        if data != barcodeData:
            data = barcodeData
            
            if data == go:        
                #myBeep.beep(0.1)
                car_go_back(500)
                next_time = 1000
                
            elif data == back:                
                #myBeep.beep(0.1)
                car_go_back(-500)
                next_time = 1000
            elif data == leftturn:               
                myBeep.beep(0.1)
                car_left_turn(500)
                next_time = 1000
            elif data == rightturn:
                myBeep.beep(0.1)
                car_right_turn(-500)
                next_time = 1000
            elif data == leftrun:               
                myBeep.beep(0.1)
                car_left_right_run(500)
                next_time = 1000
            elif data == rightrun:
                car_left_right_run(-500)
                next_time = 1000
        data = ''
        barcodeData = ''
                                
                                                  
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

#二维码生成网址 https://cli.im/            
camera = cv2.VideoCapture(0)

while True:
    # 读取当前帧
    ret, frame = camera.read()
    #反转视频镜头
    #frame = cv2.flip(frame, -1)
    # 转为灰度图像
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    barcodes = pyzbar.decode(gray)#解析图片信息
    barcodeData = ''
    for barcode in barcodes:
        # 提取条形码的边界框的位置
        # 画出图像中条形码的边界框
        (x, y, w, h) = barcode.rect
        cv2.rectangle(gray, (x, y), (x + w, y + h), (0, 0, 255), 2)
 
        # 条形码数据为字节对象，所以如果我们想在输出图像上
        # 画出来，就需要先将它转换成字符串
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        
        # 绘出图像上条形码的数据和条形码类型
        text = "{} ({})".format(barcodeData, barcodeType)
        cv2.putText(gray, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    .5, (0, 0, 125), 2)               
    
    #if len(barcodeData):
        # 向终端打印条形码数据和条形码类型
        print(time.time(), "[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
    car_move()
    if mode != 1:
        mode = 1
        car_stop()
    cv2.imshow("camera", gray)
    if cv2.waitKey(5) & 0xFF == 27: #如果按了ESC就退出 当然也可以自己设置
        break
                   
#关闭摄像头
camera.release()
#关闭窗口
cv2.destroyAllWindows()
  