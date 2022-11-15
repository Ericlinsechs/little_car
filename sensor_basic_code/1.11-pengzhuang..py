#导入模块
import RPi.GPIO as GPIO
import time

#端口模式设置
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#蜂鸣器引脚定义
BEEP_PIN = 21
#传感器引脚定义
DEV_PIN = 17

#蜂鸣器鸣叫
def beep_on():
    GPIO.output(BEEP_PIN, 1)
#蜂鸣器关闭
def beep_off():
    GPIO.output(BEEP_PIN, 0)

#读取devValue的值,触发为低电平
def devValue():
    return GPIO.input(DEV_PIN)

#初始化设备引脚
def setup_dev():
    GPIO.setup(BEEP_PIN, GPIO.OUT, initial = 0)
    GPIO.setup(DEV_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def destory():
    beep_off()
    GPIO.cleanup()
    
#循环检测
def loop_dev():
    if(devValue() == 0):
        time.sleep(0.02)
        if(devValue() == 0):
            print(">Dev get Low")
            beep_on()
            while(devValue() == 0):
                pass
            beep_off()
            print(">>>Dev get High")
            
#程序反复执行处
if __name__ == "__main__":
    setup_dev()
    try:
        while True:
            loop_dev()
    except KeyboardInterrupt:
        destory()