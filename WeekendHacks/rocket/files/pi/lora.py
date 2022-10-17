
# Pi -> LoRa
# Pi Pin MOSI -> LoRa MOSI
# Pi Pin MISO -> LoRa MISO
# Pi Pin SCK  -> LoRa SCK
# Pi Pin 25 -> LoRa CS
# Pi Pin 5 -> LoRa RST
# Pi Pin CE1 -> LoRa G0
# Pi Pin 3.3v  -> LoRa VIN
# Pi Pin GND -> LoRa GND

import time
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
import adafruit_rfm9x
import requests
import os
import json

URL = os.getenv('URL')
print(URL)

if (URL is None):
  print("URL environment variable not found")

flight_file = open("lora.log", "a+")

# Configure LoRa Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 433.0)#915.0)
rfm9x.tx_power = 23

def get_val(data, name):
   index = data.index(name)

   if index != None:
     return data[index + 1]

   return None

def make_json(data, fields):
   result = {}

   for i in range(len(fields)):
     name = fields[i]
     result[name] = get_val(data, name)

   return result

while True:
    packet = None
    rssi = rfm9x.last_rssi

    # check for packet rx
    packet = rfm9x.receive(with_header=True)
    if packet is None:
        print("waiting")
    else:
        try:
          print(packet)
          packet_text = str(packet, "ascii")
          print(packet_text)
          data = packet_text.split(",")
          print(data)

          print(get_val(data, "x"), get_val(data, "y"), get_val(data, "z"))

          fields = ['id', 'x', 'y', 'z']
          j = make_json(data, fields)
          j["signal"] = "{0} dB".format(rssi)

          if (URL is not None):
            response = requests.post(URL, json = j)

          flight_file.write(json.dumps(j))
          flight_file.write(",\n")
        except:
          print("except")
