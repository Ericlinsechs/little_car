import pigpio
import time

pi = pigpio.pi()
servo_flag = 0
systick_ms_bak = 0

def loop_pwm_servo():
    global systick_ms_bak, servo_flag
    if(int((time.time() * 1000))- systick_ms_bak > 2000):
        systick_ms_bak = int((time.time() * 1000))
        if servo_flag:
            pi.set_servo_pulsewidth(7, 1000)
            pi.set_servo_pulsewidth(16, 1000)
            pi.set_servo_pulsewidth(20, 1000)
            pi.set_servo_pulsewidth(19, 1000)
            pi.set_servo_pulsewidth(5, 1000)
            pi.set_servo_pulsewidth(6, 1000)
            pi.set_servo_pulsewidth(13, 1000)
            pi.set_servo_pulsewidth(12, 1000)
            pi.set_servo_pulsewidth(26, 1000)
        else:
            pi.set_servo_pulsewidth(7, 2000)
            pi.set_servo_pulsewidth(16, 2000)
            pi.set_servo_pulsewidth(20, 2000)
            pi.set_servo_pulsewidth(19, 2000)
            pi.set_servo_pulsewidth(5, 2000)
            pi.set_servo_pulsewidth(6, 2000)
            pi.set_servo_pulsewidth(13, 2000)
            pi.set_servo_pulsewidth(12, 2000)
            pi.set_servo_pulsewidth(26, 2000)

        servo_flag = not servo_flag
        
if __name__ == '__main__':
    try:
        while True:
            loop_pwm_servo()
    except KeyboardInterrupt:
        pass
            
        
    