#include <Adafruit_MotorShield.h>
#include <Wire.h>
#include <Servo.h>


int servoPin = 6;
int inPin = 5;

int i2cAddress = 0x8;
Adafruit_MotorShield shield = Adafruit_MotorShield();
Adafruit_StepperMotor *motor = shield.getStepper(200, 2);
Servo servo;


void setup() {
  Serial.begin(9600);

  // pin, min pulse width in microseconds, max pulse width in microseconds
  servo.attach(servoPin, 0, 180);

  // create with the default frequency 1.6KHz
  if (!shield.begin()) {
    Serial.println("Could not find Motor Shield. Check wiring.");
    while (1);
  }
  
  Serial.println("Motor Shield found.");
  motor->setSpeed(5);  // rpm
  pinMode(inPin, INPUT);
  delay(3000);
  Serial.println("starting");
}

int val = 0;
int steps = 16;

void loop() {
  delay(1000);
  val = digitalRead(inPin);
  if (val == HIGH) {
    Serial.println("on");
    //motor->step(steps, FORWARD, SINGLE);
    //motor->step(50, FORWARD, MICROSTEP);
    motor->step(steps, FORWARD, MICROSTEP);
  } else {
    Serial.println("off");
  }
}
