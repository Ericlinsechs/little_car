#导包
import RPi.GPIO as GPIO
import time

#全局變量
systick_ms_bak = 0

#端口模式设置
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#引脚定义 
XJ1_PIN = 17
XJ2_PIN = 23
BEEP_PIN = 21

#蜂鸣器鸣叫
def on():
    GPIO.output(BEEP_PIN, 1)

#蜂鸣器关闭
def off():
    GPIO.output(BEEP_PIN, 0)
    
#读取xj1的值,按键按下为低电平
def xj1():
    return GPIO.input(XJ1_PIN)

#读取xj2的值,按键按下为低电平
def xj2():
    return GPIO.input(XJ2_PIN)

#初始化按键引脚
def setup():
    GPIO.setup(BEEP_PIN,GPIO.OUT,initial = 0)
    GPIO.setup(XJ1_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(XJ2_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#循环检测按键引脚，xj1控制led1的亮灭，xj2控制蜂鸣器的响声
def loop():
    if xj1() == 0 and xj2() == 0:
        off()
        print("00")           
    elif xj1() == 0 and xj2() == 1:
        on()
        print("01")
    elif xj1() == 1 and xj2() == 0:
        on()
        print("10")
    else:
        off()
        print("11")
        
def destory():
    off()
    GPIO.cleanup()
    
    
#程序反复执行处
if __name__ == "__main__":
    setup()
    time.sleep(1)
    try:
        while True:
            loop()
    except KeyboardInterrupt:
        destory()
    