
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

# Configure LoRa Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 433.0)
rfm9x.tx_power = 23

while True:
    packet = None
    packet = rfm9x.receive(with_header=True)
    if packet is None:
        print("waiting")
    else:
        try:
          print(packet)
          packet_text = str(packet, "ascii")
          print(packet_text)
          print(packet_text.split(","))
        except:
          print("except")

    rssi = rfm9x.last_rssi
    print("Received signal strength: {0} dB".format(rssi))
