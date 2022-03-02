#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import socket
import requests
import json

outPin = 16

GPIO.setmode(GPIO.BCM)
GPIO.setup(outPin, GPIO.OUT)

time.sleep(2)
GPIO.output(outPin, GPIO.LOW)

GPIO.cleanup()

GPIO.setmode(GPIO.BCM)
GPIO.setup(outPin, GPIO.OUT)

while True:
    time.sleep(1)

    try:
        data = {'status': 'green'}
        headers = {'Content-type': 'application/json'}
        response = requests.post('http://<ServerIP>/whattodo', data = json.dumps(data), headers = headers)
        print(response)

        if response.json()["gimme"] == True:
            print("launch candy")
            GPIO.output(outPin, GPIO.HIGH)
            time.sleep(10)
            GPIO.output(outPin, GPIO.LOW)
            time.sleep(1)
            print('good')
            time.sleep(1)

    except socket.error:
        print("error")


GPIO.cleanup()
