
//Board: Arduino Mega 2560
//Processor: ATMega 2560

// LoRa
// https://www.adafruit.com/product/3073
// ATMega2650 ->LoRa
// MISO-pin 50 ->LoRa MISO
// MOSI-pin 51 ->LoRa MOSI
// SCK- Pin 52 ->LoRa SCK
// Pin 7 ->LoRa CS
// Pin 6 ->LoRa RST
// Pin 2 ->LoRa G0
// SS- pin 53 //N/A
//
// Arduino Micro ->LoRa
// MISO-pin 50 ->LoRa MISO
// MOSI-pin 51 ->LoRa MOSI
// SCK- Pin 52 ->LoRa SCK
// Pin 9 ->LoRa CS
// Pin 8 ->LoRa RST
// Pin 7 ->LoRa G0
// 3.3v ->LoRa 3.3v
// GND ->Lora GND
#include <SPI.h>
#include "LoRa.h"

const int csPin = 9; // LoRa radio chip select
const int resetPin = 8; // LoRa radio reset
const int irqPin = 7; // interrupt request pin

const byte localAddress = 0xBB;
const byte destinationAddress = 0xFF;
const byte syncWord = 0xB4; // Sync word (network ID)
const byte spreadingFactor = 7; //spreading factor (6-12)


// Accelerometer
// https://learn.sparkfun.com/tutorials/sparkfun-qwiic-3-axis-accelerometer-adxl313-hookup-guide?_ga=2.60797357.1096858093.1651183108-2026033215.1651006494
// Arduino Micro -> Accelerometer
// Pin 3 -> ADXL313 SCL
// Pin 2 -> ADXL313 SDA
// 3.3v ->ADXL313 3.3v
// GND ->ADXL313 GND
#include <Wire.h>
#include <SparkFunADXL313.h>
ADXL313 myAdxl;
const int accelerometerIC2Address = 0x1D;

// GPS
// https://www.adafruit.com/product/746
// Arduino Micro -> GPS
// Pin 6 -> GPS TX
// Pin 5 -> GPS RX
// 3.3v ->GPS 3.3v
// GND ->GPS GND
//#include <Adafruit_GPS.h>
//#include <SoftwareSerial.h>
//
//SoftwareSerial GPSSerial(6, 5);
//Adafruit_GPS GPS(&GPSSerial);
//uint32_t timer = millis();

void setup() {
  Serial.begin(115200); // initialize serial

  //--------------------------------------------------------------------------------
  // Initialize LoRa
  Serial.println("LoRa Duplex Init");
  LoRa.setPins(csPin, resetPin, irqPin); // set CS, reset, IRQ pin
  
  if (!LoRa.begin(433E6)) { // 915E6)) { // initialize ratio at 915 MHz
    Serial.println("Error LoRa init failed");
    while (true);
  }
  
  LoRa.setSyncWord(syncWord);
  LoRa.setSpreadingFactor(spreadingFactor);
  LoRa.setTimeout(10); //set Stream timeout of 10ms
  Serial.println("LoRa init succeeded"); //set the I/O pin modes:

  //--------------------------------------------------------------------------------
  // Initialize Accelerometer
  Serial.println("Accelerometer Init");
  Wire.begin(accelerometerIC2Address);

  //Begin communication over I2C
  if (myAdxl.begin() == false) {
    Serial.println("Error accelerometer init failed");
    while(1);
  }

  Serial.print("Accelerometer init succeeded");
  myAdxl.measureModeOn(); // wakes up the sensor from standby and put it into measurement mode

  //--------------------------------------------------------------------------------
  // Initialize GPS
//  Serial.println("GPS Software Serial");
//  GPS.begin(9600);
//  // uncomment this line to turn on RMC (recommended minimum) and GGA (fix data) including altitude
//  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
//  // uncomment this line to turn on only the "minimum recommended" data
//  //GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCONLY);
//  // For parsing data, we don't suggest using anything but either RMC only or RMC+GGA since
//  // the parser doesn't care about other sentences at this time
//
//  // Set the update rate
//  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);   // 1 Hz update rate
//  // For the parsing code to work nicely and have time to sort thru the data, and
//  // print it out we don't suggest using anything higher than 1 Hz
//
//  // Request updates on antenna status, comment out to keep quiet
//  GPS.sendCommand(PGCMD_ANTENNA);
//
//  delay(1000);
//  // Ask for firmware version
//  GPSSerial.println(PMTK_Q_RELEASE);
}

int counter = 0;

void sendData(String name, String value) {
  String packet = "," + name + "," + value;
  Serial.print(packet);
  LoRa.print(packet);
}

void loop() {
//  char c = GPS.read();
//
//  if (c)
//    Serial.write(c);
//
//  // if a sentence is received, we can check the checksum, parse it...
//  if (GPS.newNMEAreceived()) {
//    // a tricky thing here is if we print the NMEA sentence, or data
//    // we end up not listening and catching other sentences!
//    // so be very wary if using OUTPUT_ALLDATA and trytng to print out data
//    //Serial.println(GPS.lastNMEA());   // this also sets the newNMEAreceived() flag to false
//
//    if (!GPS.parse(GPS.lastNMEA())) {   // this also sets the newNMEAreceived() flag to false
//      Serial.println("GPS FAILED");
//      return;  // we can fail to parse a sentence in which case we should just wait for another
//    }
//  }
 
  if (!myAdxl.dataReady()) {// check data ready interrupt, note, this clears all other int bits in INT_SOURCE reg
    Serial.println("Waiting for dataReady.");
  }
  else {
    myAdxl.readAccel();
    
    // send packet
    LoRa.beginPacket();
    LoRa.print("BEGIN,");
    sendData("id", String(counter));
    sendData("src", String(localAddress));
    sendData("dest", String(destinationAddress));
    sendData("x", String(myAdxl.x));
    sendData("y", String(myAdxl.y));
    sendData("z", String(myAdxl.z));
//    sendData("day", String(GPS.day, DEC));
//    sendData("month", String(GPS.month, DEC));
//    sendData("year", String(GPS.year, DEC));
//    sendData("fix", String((int)GPS.fix));
//    sendData("quality", String((int)GPS.fixquality));
//    
//    if (GPS.fix) {
//      sendData("latitude", String(GPS.latitude, 4));
//      sendData("lat", String(GPS.lat));
//      sendData("longitude", String(GPS.longitude, 4));
//      sendData("long", String(GPS.lon));
//      sendData("knots", String(GPS.speed));
//      sendData("angle", String(GPS.angle));
//      sendData("altitude", String(GPS.altitude));
//      sendData("satellites", String((int)GPS.satellites));
//    }
    LoRa.print(",END");
    Serial.println();
    LoRa.endPacket();
  }
  
  
  counter++;
  delay(50);
}
