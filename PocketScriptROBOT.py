#!/usr/bin/python
 
import sys, os, pyaudio, time, socket, fcntl, struct
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *
import RPi.GPIO as GPIO
from threading import Thread
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

class Publisher(Thread):
    def run(self):
        def getHwAddr(ifname):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
            return '-'.join(['%02x' % ord(char) for char in info[18:24]])
        try:
            MQTT_SERVER = "iot.eclipse.org"
            mac = getHwAddr('wlan0')
            MQTT_PATH = ("voice_mqtt/measurements/" +str(mac))
            global rpm
            count = 0
            while True:
                count += 1
                #print(count)
                if (count >= 60):
                    print("RPM: ", rpm)
                    publish.single(MQTT_PATH, "RPM of robot: " +str(rpm), hostname=MQTT_SERVER)
                    count = 0
                    rpm = 0
                time.sleep(1)
        except KeyboardInterrupt:
            GPIO.cleanup()
            #set event that causes it to gracefully quit

class Subscriber(Thread):

    def run(self):
        def on_connect(client, userdata, flags, rc):
            print("Connected with result code "+str(rc))
            client.subscribe(MQTT_PATH)
 
        def on_message(client, userdata, msg):
            global control
            print(msg.topic+" "+str(msg.payload))
            phrase = msg.payload
            control = command_execution(phrase, control)

        try:
            global mac
            control = False
            MQTT_SERVER = "iot.eclipse.org"
            MQTT_PATH = ("voice_mqtt/commands/"+str(mac))
            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(MQTT_SERVER, 1883, 60)
            client.loop_forever()
        except KeyboardInterrupt:
            GPIO.cleanup()
            #set event that causes it to gracefully quit

#---------defs------------

def getHwAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return '-'.join(['%02x' % ord(char) for char in info[18:24]])

def rpm_increment(tachometerpin): # event detect callback, on separate thread
    global rpm
    rpm += 1
    #print(rpm) # tachometer debugging
    
def blinkdiode():
    GPIO.output(ledpin, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(ledpin, GPIO.LOW)
    time.sleep(1)
    GPIO.output(ledpin, GPIO.HIGH)
    time.sleep(1)
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
    GPIO.output(motorpins, GPIO.LOW)
    
def leftturn():
    GPIO.output(right1, GPIO.LOW)
    GPIO.output(right2, GPIO.LOW)
    GPIO.output(left1, GPIO.HIGH)
    GPIO.output(left2, GPIO.LOW)

def rightturn():
    GPIO.output(right1, GPIO.HIGH)
    GPIO.output(right2, GPIO.LOW)
    GPIO.output(left1, GPIO.LOW)
    GPIO.output(left2, GPIO.LOW)

def changespeed(dc):
    motor1.ChangeDutyCycle(dc)
    motor2.ChangeDutyCycle(dc)

def invalidcommand():
    print("Control word must be said before commands")
    
def command_execution(phrase, control):
    print ("Detected keyword, restarting search")
    # command execution
    
    if (phrase == 'BLINK DIODE '):
        blinkdiode()
        print('Blinking diode')
        
    elif (phrase == 'BEGIN '):
        control = True
        print('Control word accepted')
        
    elif (phrase == 'STOP '):
        stop()
        control = False
        print('Stopping')
        
    elif (phrase == 'DRIVE '):
        if (control == True):
            forward()
            print('Going forward')
        else:
            invalidcommand()
            
    elif (phrase == 'BACK '):
        if (control == True):
            backward()
            print('Going backward')
        else:
            invalidcommand()
            
    elif (phrase == 'LEFT '):
        if (control == True):
            leftturn()
            print('Turning left')
        else:
            invalidcommand()
            
    elif (phrase == 'RIGHT '):
        if (control == True):
            rightturn()
            print('Turning right')
        else:
            invalidcommand()
            
    elif (phrase == 'FIRST '):
        if (control == True):
            changespeed(25)
            print('Changed duty cycle to 25')
        else:
            invalidcommand()
            
    elif (phrase == 'SECOND '):
        if (control == True):
            changespeed(50)
            print('Changed duty cycle to 50')
        else:
            invalidcommand()
        
    elif (phrase == 'THIRD '):
        if (control == True):
            changespeed(75)
            print('Changed duty cycle to 75')
        else:
            invalidcommand()
            
    elif (phrase == 'FOURTH '):
        if (control == True):
            changespeed(99)
            print('Changed duty cycle to 99')
        else:
            invalidcommand()

    return control        

#-----motor setup----------

GPIO.setmode(GPIO.BCM)

ledpin = 4
enable1 = 17
enable2 = 23
left1 = 27
left2 = 22
right1 = 25
right2 = 24

tachometerpin = 26

enablerpins = [enable1,enable2]
motorpins = [left1,left2,right1,right2]

GPIO.setup(enablerpins, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(motorpins, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(ledpin, GPIO.OUT, initial=GPIO.LOW)

GPIO.setup(tachometerpin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

motor1 = GPIO.PWM(enable1,25)
motor1.start(25)

motor2 = GPIO.PWM(enable2,25)
motor2.start(25)

#------PocketSphinx setup----------

modeldir = "/home/pi/pocketsphinx-5prealpha/model/"

config = Decoder.default_config()
config.set_string('-hmm', os.path.join(modeldir, 'en-us/en-us'))
config.set_string('-dict', '/home/pi/pocketsphinx-python/keyphrase.dic')
config.set_string('-kws', '/home/pi/pocketsphinx-python/keyphrase.list')
config.set_float('-samprate', 16000.0)
config.set_int('-nfft', 512)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True,  frames_per_buffer=1024)
stream.start_stream()

decoder = Decoder(config)
decoder.start_utt()
try:
    mac = getHwAddr('wlan0')
    Publisher().start()
    Publisher.daemon = True
    Subscriber().start()
    Subscriber.daemon = True
    rpm = 0
    GPIO.add_event_detect(tachometerpin, GPIO.FALLING, callback=rpm_increment, bouncetime=200)
    blinkdiode()
    print("Ready to listen")
    control = False
    while True:
        
        if (control == True):
            GPIO.output(ledpin, GPIO.HIGH)
        else:
            GPIO.output(ledpin, GPIO.LOW)
                        
        buf = stream.read(1024, exception_on_overflow = False)

        decoder.process_raw(buf, False, False)

        if decoder.hyp() != None:
            print ([(seg.word) for seg in decoder.seg()])
            #print ([(seg.word, seg.prob, seg.start_frame, seg.end_frame) for seg in decoder.seg()])
            control = command_execution(seg.word, control)

            decoder.end_utt()
            time.sleep(0.02)
            decoder.start_utt()
        
except KeyboardInterrupt:
    print("Exception: KeyboardInterrupt")
    GPIO.cleanup()
