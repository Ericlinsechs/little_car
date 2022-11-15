#导入模块
import RPi.GPIO as GPIO
import time

#端口模式设置
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#蜂鸣器引脚定义
BEEP_PIN = 17

#初始化蜂鸣器
def setup_beep():
    GPIO.setup(BEEP_PIN,GPIO.OUT,initial = 0)
    
#蜂鸣器关闭
def beep_on():
    GPIO.output(BEEP_PIN, 0)
    
#蜂鸣器鸣叫
def beep_off():
    GPIO.output(BEEP_PIN, 1)

#释放引脚         
def destory():
    beep_off()
    GPIO.cleanup()
#蜂鸣器循环
def beep(x):
    beep_on()
    time.sleep(x)
    beep_off()
    time.sleep(x)
#程序反复执行处
if __name__ == "__main__":
    setup_beep()
    try:
        while True:
            beep(0.5)
    except KeyboardInterrupt:
        destory()