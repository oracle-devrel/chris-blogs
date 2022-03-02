#!/usr/bin/python3
import time
import sys
import RPi.GPIO as GPIO
import os


shutdownPin = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(shutdownPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def Shutdown(channel):
    print("Shutting Down")
    time.sleep(5)
    os.system("sudo shutdown -h now")
    
GPIO.add_event_detect(shutdownPin, GPIO.FALLING, callback=Shutdown, bouncetime=2000)

while True:
    time.sleep(1)
