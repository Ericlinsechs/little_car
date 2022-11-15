#导入模块
import RPi.GPIO as GPIO
import time

#端口模式设置
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#引脚定义
LEDR_PIN = 9
LEDG_PIN = 8
LEDB_PIN = 11

#点亮LED 参数led_pin 为引脚编号
def on(led_pin):
    if led_pin == 0:
        GPIO.output(LEDR_PIN, 1)
    elif led_pin == 1:
        GPIO.output(LEDG_PIN, 1)
    elif led_pin == 2:
        GPIO.output(LEDB_PIN, 1)
        
#熄灭LED 参数led_pin 为引脚编号
def off(led_pin):
    if led_pin == 0:
        GPIO.output(LEDR_PIN, 0)
    elif led_pin == 1:
        GPIO.output(LEDG_PIN, 0)
    elif led_pin == 2:
        GPIO.output(LEDB_PIN, 0)

#初始化LED灯
def setup_led():
    GPIO.setup(LEDR_PIN, GPIO.OUT, initial = 0)
    GPIO.setup(LEDG_PIN, GPIO.OUT, initial = 0)
    GPIO.setup(LEDB_PIN, GPIO.OUT, initial = 0)

#大循环LED灯
def loop_led():    
    for i in range(3):
        on(i)
        time.sleep(1)
        off(i)
#释放IO口        
def destory():
    off(0)
    off(1)
    off(2)
    GPIO.cleanup
#程序反复执行处
if __name__ == "__main__":
    setup_led()
    try:
        while True:
            loop_led()
    except KeyboardInterrupt:     
        destory()
