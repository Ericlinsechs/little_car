#导包
import RPi.GPIO as GPIO
import time

#端口模式设置
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#全局变量定义
key_flag = 0
systick_ms_bak = 0
#风扇引脚定义
FSA_PIN = 17
FSB_PIN = 18
#按键引脚定义 
KEY1_PIN = 24
KEY2_PIN = 25

#风扇开启
def fs_on(chn):
    if chn == 0:
        GPIO.output(FSA_PIN, 0)
    if chn == 1:
        GPIO.output(FSB_PIN, 0)
   
#风扇关闭
def fs_off(chn):
    if chn == 0:
        GPIO.output(FSA_PIN, 1)
    if chn == 1:
        GPIO.output(FSB_PIN, 1)
        
#读取KEY的值,按键按下为低电平
def key(chn):
    if chn == 0:
        return GPIO.input(KEY1_PIN)
    if chn == 1:
        return GPIO.input(KEY2_PIN)
        
#初始化按键引脚
def setup_key():
    GPIO.setup(FSA_PIN, GPIO.OUT, initial = 1)
    GPIO.setup(FSB_PIN, GPIO.OUT, initial = 1)
    GPIO.setup(KEY1_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(KEY2_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#循环检测按键引脚,控制风扇
def loop_key():
        if key(0) == 0 and key(1) == 1:
            time.sleep(0.02)
            if key(0) == 0:
                fs_on(0)
                fs_off(1) 
        if key(1) == 0 and key(0) == 1:  
            time.sleep(0.02)
            if key(1) == 0:
                fs_on(1)
                fs_off(0)
        if key(0) == 0 and key(1) == 0:
            fs_off(1)
            fs_off(0)

#释放IO口            
def destory():
    fs_off(0)
    fs_off(1)
    GPIO.cleanup()
            
#程序反复执行处
if __name__ == "__main__":
    setup_key()

    try:
        while True:
            loop_key()
    except KeyboardInterrupt:
        destory()