#导入模块
import RPi.GPIO as GPIO
import time

#端口模式设置
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#蜂鳴器引脚定义
BEEP_PIN = 21
#按键引脚定义 
KEY_PIN = 17
#蜂鸣器鸣叫
def beep_on():
    GPIO.output(BEEP_PIN, 1)   
#蜂鸣器关闭
def beep_off():
    GPIO.output(BEEP_PIN, 0)
#读取KEY1的值,按键按下为高电平
def key():
    return GPIO.input(KEY_PIN)
#初始化按键引脚
def setup_key():
    GPIO.setup(BEEP_PIN, GPIO.OUT, initial = 0)    #蜂鸣器引脚设置为输出模式，初始状态为低电平
    GPIO.setup(KEY_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)    #按键引脚设为上拉输入模式

#循环检测按键引脚,控制蜂鸣器的响声
def loop_key():
    if(key() == 1):
        time.sleep(0.02)
        if(key() == 1):
            beep_on()
            while(key() == 1):
                pass
            beep_off()
#IO口释放            
def destory():
    beep_off()
    GPIO.cleanup()           
#程序反复执行处
if __name__ == "__main__":
    setup_key()
    try:
        while True:
            loop_key()
    except KeyboardInterrupt:
        destory()
    
