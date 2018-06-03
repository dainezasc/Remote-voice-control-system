#!/usr/bin/python

import sys, tty, termios, time
import RPi.GPIO as GPIO



GPIO.setmode(GPIO.BCM)



ledpin = 4


enable1 = 17
enable2 = 23
left1 = 27
left2 = 22
right1 = 25
right2 = 24

GPIO.setup(ledpin, GPIO.OUT, initial=GPIO.LOW)


GPIO.setup(enable1, GPIO.OUT, initial=GPIO.HIGH)


GPIO.setup(enable2, GPIO.OUT, initial=GPIO.HIGH)


GPIO.setup(left1, GPIO.OUT, initial=GPIO.LOW)


GPIO.setup(left2, GPIO.OUT, initial=GPIO.LOW)


GPIO.setup(right1, GPIO.OUT, initial=GPIO.LOW)


GPIO.setup(right2, GPIO.OUT, initial=GPIO.LOW)




motor1 = GPIO.PWM(17,25) # set motor1 pwm frequency here

motor1.start(25)



motor2 = GPIO.PWM(23,25) # set motor2 pwm frequency here

motor2.start(25)




def getch():

    fd = sys.stdin.fileno()

    old_settings = termios.tcgetattr(fd)

    try:

        tty.setraw(sys.stdin.fileno())

        ch = sys.stdin.read(1)

    finally:

        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return ch

def blinkdiode():
    GPIO.output(ledpin, GPIO.HIGH)

    time.sleep(2)

    GPIO.output(ledpin, GPIO.LOW)

    time.sleep(2)

    GPIO.output(ledpin, GPIO.HIGH)

    time.sleep(2)
    GPIO.output(ledpin, GPIO.LOW)


def forward():
    GPIO.output(left1, GPIO.HIGH)

    GPIO.output(left2, GPIO.LOW)

    GPIO.output(right1, GPIO.HIGH)
    GPIO.output(right2, GPIO.LOW)

def backward():
    GPIO.output(left1, GPIO.LOW)

    GPIO.output(left2, GPIO.HIGH)

    GPIO.output(right1, GPIO.LOW)
    GPIO.output(right2, GPIO.HIGH)

def stop():
    GPIO.output(left1, GPIO.LOW)

    GPIO.output(left2, GPIO.LOW)

    GPIO.output(right1, GPIO.LOW)
    GPIO.output(right2, GPIO.LOW)


def leftturn():
    GPIO.output(left1, GPIO.LOW)

    GPIO.output(left2, GPIO.LOW)

    GPIO.output(right1, GPIO.HIGH)
    GPIO.output(right2, GPIO.LOW)


def rightturn():
    GPIO.output(left1, GPIO.HIGH)

    GPIO.output(left2, GPIO.LOW)

    GPIO.output(right1, GPIO.LOW)
    GPIO.output(right2, GPIO.LOW)

def speed25():
    motor1.ChangeDutyCycle(25)
    motor2.ChangeDutyCycle(25)

def speed50():
    motor1.ChangeDutyCycle(50)
    motor2.ChangeDutyCycle(50)

def speed75():
    motor1.ChangeDutyCycle(75)
    motor2.ChangeDutyCycle(75)

def speed100():
    motor1.ChangeDutyCycle(99)
    motor2.ChangeDutyCycle(99)    

try:

    print ("Program started. Press X or say 'exit program' to exit")

    while(True):

        char = getch()


        if(char == "b"):
            blinkdiode()
        if(char == "w"):

            forward()
        if(char == "s"):

            backward()
        if(char == "q"):

            stop()
        if(char == "a"):

            leftturn()
        if(char == "d"):

            rightturn()
        if(char == "1"):
            print ("Changed duty cycle to 25")
            speed25()

        if(char == "2"):
            print ("Changed duty cycle to 50")
            speed50()
        if(char == "3"):
            print ("Changed duty cycle to 75")
            speed75()
        if(char == "4"):
            print ("Changed duty cycle to 100")
            speed100()    
        if(char == "x"):

            raise KeyboardInterrupt

except KeyboardInterrupt:

    GPIO.cleanup()

