#!/usr/bin/python
 
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

tachometerpin = 26
enable2 = 23
right1 = 25
right2 = 24

GPIO.setup(tachometerpin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(enable2, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(right1, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(right2, GPIO.OUT, initial=GPIO.LOW)

motor2 = GPIO.PWM(enable2,25)
motor2.start(100)

def rpm_increment(tachometerpin):
    global rpm
    rpm += 1
    print("Current RPM: ", rpm)

try:
    rpm = 0
    count = 0
    GPIO.add_event_detect(tachometerpin, GPIO.FALLING, callback=rpm_increment, bouncetime=200)
    while True:
        count += 1
        print(count)
        if (count >= 60):
            print("RPM: ", rpm)
            # publish rpm
            count = 0
            rpm = 0
        time.sleep(1)    

except KeyboardInterrupt:
    print("Exception: KeyboardInterrupt")
    GPIO.cleanup()
