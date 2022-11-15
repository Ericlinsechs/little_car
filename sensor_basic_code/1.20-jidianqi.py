#导包
import RPi.GPIO as GPIO
import time

#端口模式设置
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#全局变量定义
key_falg = 0

#继电器引脚定义
JDQ_PIN = 17
#按键引脚定义 
KEY_PIN = 24

#继电器闭合
def jdq_on():
    GPIO.output(JDQ_PIN, 0)
    
#继电器断开
def jdq_off():
    GPIO.output(JDQ_PIN, 1)

#读取KEY的值,按键按下为低电平
def key():
    return GPIO.input(KEY_PIN)

#初始化按键引脚
def setup_key():
    GPIO.setup(JDQ_PIN, GPIO.OUT)
    GPIO.setup(KEY_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#循环检测按键引脚,控制继电器
def loop_key():
    global key_falg
    if key() == 0 and key_falg == 0:
        time.sleep(0.02)
        if(key() == 0):
            key_falg = 1
            jdq_on()
            while(key() == 0):
                pass               
    elif key() == 0 and key_falg == 1:
        time.sleep(0.02)
        if(key() == 0):
            key_falg = 0
            jdq_off()
            while(key() == 0):
                pass 
            
def destory():
    jdq_off()
    GPIO.cleanup()
            
#程序反复执行处
if __name__ == "__main__":
    setup_key()

    try:
        while True:
            loop_key()
    except KeyboardInterrupt:
        destory()
    

