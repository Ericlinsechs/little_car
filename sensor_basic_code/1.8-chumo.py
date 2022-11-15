#导入模块
import RPi.GPIO as GPIO
import time

#端口模式设置
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#蜂鳴器引脚定义
BEEP_PIN = 21
#傳感器引腳定義
DEV_PIN = 17

#蜂鸣器鸣叫
def beep_on():
    GPIO.output(BEEP_PIN, 1)
    
#蜂鸣器关闭
def beep_off():
    GPIO.output(BEEP_PIN, 0)

#读取devValue的值,触发为高电平
def devValue():
    return GPIO.input(DEV_PIN)

#初始化设备引脚
def setup_dev():
    GPIO.setup(BEEP_PIN, GPIO.OUT, initial = 0)
    GPIO.setup(DEV_PIN, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#循环检测
def loop_dev():
    if(devValue() == 1):
        time.sleep(0.02)
        if(devValue() == 1):
            print(">Dev get High")
            beep_on()
            while(devValue() == 1):
                pass
            beep_off()
            print(">>>Dev get Low")
#IO口释放
def destory():
    beep_off()
    GPIO.cleanup()
            
#程序反复执行处
if __name__ == "__main__":
    setup_dev()
    try:
        while True:
            loop_dev()
    except KeyboardInterrupt:
        destory()
    
