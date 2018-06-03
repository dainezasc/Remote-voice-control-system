#!/usr/bin/python

import sys, os, pyaudio, time, socket, fcntl, struct
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *
import RPi.GPIO as GPIO
from threading import Thread
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

class Subscriber(Thread):

    def run(self):
        def on_connect(client, userdata, flags, rc):
            print("Connected with result code "+str(rc))
            client.subscribe(MQTT_PATH)
 
        def on_message(client, userdata, msg):
            print(msg.topic+" "+str(msg.payload))
        try:
            MQTT_SERVER = "iot.eclipse.org"
            MQTT_PATH = "voice_mqtt/measurements/#"
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
        
def blinkdiode():
    GPIO.output(ledpin, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(ledpin, GPIO.LOW)
    time.sleep(2)
    GPIO.output(ledpin, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(ledpin, GPIO.LOW)

def invalidcommand():
    print("Control word must be said before commands")

#-----LED setup (optional)----------

GPIO.setmode(GPIO.BCM)

ledpin = 4

GPIO.setup(ledpin, GPIO.OUT, initial=GPIO.LOW)
    
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
    Subscriber().start()
    Subscriber.daemon = True
    mac = raw_input("Type MAC address of robot you want to control.\n")
    print("Connection set to: " +str(mac))
    MQTT_SERVER = "iot.eclipse.org"
    MQTT_PATH = ("voice_mqtt/commands/" +str(mac))
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
            print ("Detected keyword, restarting search")
            # command execution
            
            if (seg.word == 'BLINK DIODE '):
                blinkdiode()
                print('Blinking diode')
                
            elif (seg.word == 'BEGIN '):
                control = True
                publish.single(MQTT_PATH, seg.word, hostname=MQTT_SERVER)
                print('Control word accepted')
                
            elif (seg.word == 'STOP '):
                control = False
                publish.single(MQTT_PATH, seg.word, hostname=MQTT_SERVER)
                print('Stopping')
                
            elif (seg.word == 'DRIVE '):
                    publish.single(MQTT_PATH, seg.word, hostname=MQTT_SERVER)
                    print('Going forward')
                    if (control == False):
                        invalidcommand()
                    
            elif (seg.word == 'BACK '):
                    publish.single(MQTT_PATH, seg.word, hostname=MQTT_SERVER)
                    print('Going backward')
                    if (control == False):
                        invalidcommand()
                    
            elif (seg.word == 'LEFT '):
                    publish.single(MQTT_PATH, seg.word, hostname=MQTT_SERVER)
                    print('Turning left')
                    if (control == False):
                        invalidcommand()
                    
            elif (seg.word == 'RIGHT '):
                    publish.single(MQTT_PATH, seg.word, hostname=MQTT_SERVER)
                    print('Turning right')
                    if (control == False):
                        invalidcommand()
                    
            elif (seg.word == 'FIRST '):
                    publish.single(MQTT_PATH, seg.word, hostname=MQTT_SERVER)
                    print('Changed duty cycle to 25')
                    if (control == False):
                        invalidcommand()
                    
            elif (seg.word == 'SECOND '):
                    publish.single(MQTT_PATH, seg.word, hostname=MQTT_SERVER)
                    print('Changed duty cycle to 50')
                    if (control == False):
                        invalidcommand()
                
            elif (seg.word == 'THIRD '):
                    publish.single(MQTT_PATH, seg.word, hostname=MQTT_SERVER)
                    print('Changed duty cycle to 75')
                    if (control == False):
                        invalidcommand()
                    
            elif (seg.word == 'FOURTH '):
                    publish.single(MQTT_PATH, seg.word, hostname=MQTT_SERVER)
                    print('Changed duty cycle to 99')
                    if (control == False):
                        invalidcommand()
        
            decoder.end_utt()
            time.sleep(0.02)
            decoder.start_utt()
        
except KeyboardInterrupt:
    print("Exception: KeyboardInterrupt")
    GPIO.cleanup()
