#include <Wire.h>
#include <Servo.h>

int servoPin = 10;
int escPin = 11;

int i2cAddress = 0x8;

Servo esc;
Servo servo;

int status = 0;

#define ERROR_READING 1
#define INVALID_RANGE 2


void setup() {
  Serial.begin(9600);

  Wire.begin(i2cAddress);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);

  servo.attach(servoPin, 0, 180); // pin, min pulse width, max pulse width in microseconds

  esc.attach(escPin, 1500, 2000); // pin, min pulse width, max pulse width in microseconds
  esc.write(1500);                // initialize the ESC
  delay(3000);

  Serial.println("starting");
}

void loop() {
}

boolean range(int min, int max, int value) {
  return (min <= value) && (value <= max);
}

void receiveEvent(int byteCount) {
  Serial.print("receiveEvent: ");
  Serial.println(byteCount);

  if (byteCount > 1) {
    byte message = Wire.read();
 
    switch (message) {
      case 1: {
        byte degrees = Wire.read();
        Serial.print("servo: ");
        Serial.println(degrees);
          
        if (range(0, 180, degrees)) {
          servo.write(degrees);
        }
        else {
          status = INVALID_RANGE;
        }
        
        break;
      }
      
      case 2: {
        int speed = 0;   
      
        if (byteCount == 3) {
          byte high = Wire.read();
          byte low = Wire.read();
          Serial.println(high);
          Serial.println(low);
          speed = 0;
          speed = (high << 4) | low;
        }
        else {
          speed = Wire.read();
        }
        
        Serial.print("esc: ");
        Serial.println(speed);

        if (range(1000, 2000, speed)) {
          esc.write(speed);
        }
        else {
          status = INVALID_RANGE;
        }
        
        break;
      }
  
      default: {
        status = ERROR_READING;
      }
    }
  }
}

void requestEvent() {
  Serial.print("requestEvent ");
  Serial.println(status);
  Wire.write(status);
}
