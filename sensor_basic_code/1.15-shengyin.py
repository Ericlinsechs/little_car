#导入模块
import RPi.GPIO as GPIO
import time

#端口模式设置
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#LED引脚定义
LED_PIN = 4
#传感器引脚定义
DEV_PIN = 17

#led亮
def led_on():
    GPIO.output(LED_PIN, 0)
#led熄灭
def led_off():
    GPIO.output(LED_PIN, 1)

#读取devValue的值,触发为低电平
def devValue():
    return GPIO.input(DEV_PIN)

#初始化设备引脚
def setup_dev():
    GPIO.setup(LED_PIN, GPIO.OUT, initial = 1)
    GPIO.setup(DEV_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def destory():
    led_off()
    GPIO.cleanup()
    
#循环检测
def loop_dev():
    if(devValue() == 0):
        time.sleep(0.02)
        if(devValue() == 0):
            print(">Dev get Low")
            led_on()
            time.sleep(3)
            while(devValue() == 0):
                pass
            led_off()
            print(">>>Dev get High")

            
#程序反复执行处
if __name__ == "__main__":
    setup_dev()
    try:
        while True:
            loop_dev()
    except KeyboardInterrupt:
        destory()
    
