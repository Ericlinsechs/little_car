'''
图像识别功能使用前，如果树梅派在开机前有连接的摄像头，
需要先关闭mjpg进程 

请在光照环境稳定且背景为纯色的情况下使用图像识别功能。
'''

import cv2  #导入库
import time
import pyzbar.pyzbar as pyzbar
import pigpio
import os

#启动脚本杀死影响程序的进程
os.system('./killmain.sh')

#引脚定义
PIN_yuntai = 26
PIN_camera = 12


#类实例化
pi = pigpio.pi()

pi.set_servo_pulsewidth(PIN_yuntai, 1500)
pi.set_servo_pulsewidth(PIN_camera, 1500)
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
        # 向终端打印条形码数据和条形码类型
        print(time.time(), "[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))

    cv2.imshow("camera", gray)
    
    if cv2.waitKey(5) & 0xFF == 27: #如果按了ESC就退出 当然也可以自己设置
        break
#关闭摄像头
camera.release()
#关闭窗口
cv2.destroyAllWindows()
    
