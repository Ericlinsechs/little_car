import RPi.GPIO as GPIO
import time

TRIG = 17
ECHO = 18

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def distance():
    err = 0
    GPIO.output(TRIG, 0)
    time.sleep(0.000002)

    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)

    time0 = time.time()
    while GPIO.input(ECHO) == 0 and time.time()-time0<0.1:
        a = 0
    if time.time()-time0 >= 0.1:
        err = 1
        return 0
    
    
    time1 = time.time()
    while GPIO.input(ECHO) == 1  and time.time()-time1<0.1:
        a = 1
    
    if time.time()-time1 >= 0.1:
        err = 1
        return 0
    
    time2 = time.time()

    during = time2 - time1
    return during * 340 / 2 * 100

def loop():
    while True:
        dis = distance()
        print ('dis:%d cm'%dis)
        time.sleep(0.1)

def destroy():
    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
