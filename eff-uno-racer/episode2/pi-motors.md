# Pi Controlled Servo Motors
By Chris Bensen

![Pi, Arduino, IC2, Brushless Motors](breadboard.jpg)

## A Rabbit Hole

All too often someone shows something they built and maybe a short video or blog post about how it was done, but the directions are far from complete and the rationale behind the choices is lacking. The reason I’m doing this series is to show the process and the rationale behind the choices. At the end we will have something that’s pretty cool. Trust me. The problem is that things always take more time than expected. I thought I’d be a little further than where I’m currently at, but there’s been some discovery and research along the way. If everything went together smoothly, then I’d already have made one of these.

When building this, I have to balance a few things. First is getting it to work. Second is performance. If I can do both at the same time, that’s a bonus, but I can and will go back and evaluate the performance later. For this project performance comes in two flavors: response time and battery usage. This will have to be tuned, so getting things running for real-world evaluation is paramount. Third, and most important, is documenting the process. Sometimes things go smoothly and work as planned. Other times they do not. I suppose that’s why I’m doing this; to show that building things is messy and to provide some insight, education, and possibly some entertainment (because not a lot has gone right at this point).

Now, I am only one person and I don’t know everything. Anyone that claims they know everything is lying. What I do know is that I can figure things out --- and get myself into trouble. I also know how to read directions, ask friends and experts for advice, and if that fails, try, try, try again. A little bit of each went into this.

The reason I’m saying all this is I ran into few problems, four to be exact. You’ll read about my journey in this process and all of the decisions, as well as the mistakes. Those are worth mentioning here so you can look for them in the article:

- Power Supply
- Common ground
- Pi runs at 3.3v and Arduino at 5v
- Few development tools run on the Pi Zero
- [Updated Breadboard](https://www.thingiverse.com/thing:4896228)

## Setting up the Pi

At this point I have a Pi Zero, Pi spy camera, servo and ESC connected to a brushless motor. Eventually more things will be added, but this is enough to get started. I figured we'd get started by setting up the Pi.

There are a lot of ways to write an OS image to an SD card, but I have found the Raspberry Pi Imager [https://www.raspberrypi.org/software/] the easiest, especially if you want to use the standard Pi OS. I usually use [Oracle Linux](https://www.oracle.com/linux/downloads/linux-arm-downloads.html) because I have an entire operating system team to help me out, but unfortunately Oracle Linux doesn’t support the Raspberry Pi Zero (because Oracle Linux is 64-bit while the Pi Zero is 32-bit), so I’m using Pi OS.

![](PiImager.png)

The Pi Zero is pretty slow, unlike a Pi 4, so you don’t want to do your development on the device. There is where Visual Studio Code shines. However, the VS Code Remote SSH extension does not support the Pi. There are two ways that I can do this:

1.	Create a GitHub repo and edit locally on my desktop, push the changes, and pull them on the Pi
2.	Use a combination of local editor and scp for copying the local file to the pi, ssh into the Pi, and run the script.

Another problem, and one I didn’t expect, was that GraalVM does not support the Pi. For Pi 3 or Pi 4 you would do download GraalVM for Pi (ARM) and run its Java binary:

```
> wget https://github.com/graalvm/graalvm-ce-builds/releases/download/vm-21.1.0/graalvm-ce-java16-linux-aarch64-21.1.0.tar.gz

> tar -xzf graalvm-ce-java16-linux-aarch64-21.1.0.tar.gz
export PATH=/home/pi/graalvm-ce-java16-21.1.0/bin:$PATH
> java
-bash: /home/pi/graalvm-ce-java16-21.1.0/bin/java: cannot execute binary file: Exec format error
````

Ah, right, ARM-7 on a 32-bit OS. I’m beginning to see why not many developers use the Pi Zero. It may be small but it just doesn’t have the support the regular Pi has, and it’s a little low on CPU and Memory.

Well, everyone programs the Pi with Python anyway, right?

[Video](https://youtu.be/-BF6zZbBVFA)

## Unexpected Hardware: Arduino

At this point I shook my head. Just like anything, balancing a big project requires multitasking. I’ve been juggling too many other parts of the project and didn’t give the electronics a lot of focus. The Pi Zero doesn’t have PWM pins, and after a few tests with the Pi 4, the PWM signal isn’t reliable enough. This is because the Pi is running a preemptive multitasking operating system so the PWM signal --- which must be clean --- is a little sporadic, or what I like to call "herky jerky." I need a dedicated microcontroller.

Introducing an Arduino to this project isn’t trivial. I actually went back and forth a bit, but settled (for now) on an Arduino Micro. I have a few of these laying around, and they are small and fairly powerful. More on why I choose this Arduino later.

The voltage regulator I was using was rated for 2.5amp, and when I added the Arduino, the Pi was stuck in a reboot cycle due to being underpowered. What confused me is that it was working until I configured something which required a reboot, so I wasn’t looking at the voltage regulator. The other reason I wasn’t looking at the voltage regulator is that 2.5amp actually *should* be enough power, but it turned out that the combination of the monitor, USB hub, mouse, and keyboard pulled more than that. Why the monitor pulls 2amp is beyond me; it has its own power supply! This is exactly why I went to such lengths to build a custom prototype breadboard.

One problem I have is that when going between debugging at my desk and the device on the garage workbench, power and ground changes a bit, causing problems. When I moved the breadboard to my computer to debug, the power changed from only the power supply to the power supply *plus* the computer’s USB. And now the grounds are not the same. All devices that are communicating must have the same ground, but I find that switching between running the device I’m making and plugging in the USB cable for programming/debugging can affect things or require slight wiring changes. If you have a solution for this, I’d love to hear how you have solved it.

I swapped the voltage regulator and solved the power problems. In the final project I should be able to go back to the original unit, but I’m considering designing a custom PCB so this is easier to develop and assemble.

## Communicating Between Raspberry Pi and Arduino

Communicating between an RPi and an Arduino on I2C is a bit of a mess if you are using the `Wire.h` library. The short answer is that RPi is using a repetitive start signal, while Arduino is not. Repetitive start signal on the I2C interface tells the device to start answering for the call. In case of the Arduino, asking and answering is in two separated calls. Therefore, you cannot send a block. However, I found I could use the `SMBus.write_i2c_block_data()` without any problems because this is sent a bit differently. This is good, because if I had to send every byte individually, things would be really slow. After looking at this I added some optimizations; let me know in the comments if you can spot them.

Here is the Arduino [carduino.ino](carduino.ino) sketch:

```
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

  // pin, min pulse width, max pulse width in microseconds
  servo.attach(servoPin, 0, 180);

  // pin, min pulse width, max pulse width in microseconds
  esc.attach(escPin, 1500, 2000);
  esc.write(1500); // initialize the ESC
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
        byte position = Wire.read();
        Serial.print("servo: ");
        Serial.println(position);

        if (range(0, 180, position)) {
          servo.write(position);
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
```

Once the Arduino is set up and plugged into the Pi’s I2C pins --- oh wait, the Arduino is 5v and the Pi is 3.3v. Logic can be sent to the Arduino, but the Arduino can't send logic to the Pi. [Logic Level Converter](https://learn.sparkfun.com/tutorials/bi-directional-logic-level-converter-hookup-guide/all) to the rescue! This little board will convert bi-directionally without frying anything. The breadboard has a few more bits and pieces than first expected, but it’s coming along.

Connecting an I2C device to a Pi is fairly straight forward once you know how. Adafruit has a [detailed list of steps](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c):

1.	`> sudo apt-get install -y python-smbus`
2.	`> sudo apt-get install -y i2c-tools`
3.	`> sudo raspi-config`
4.	Choose Interfacing Options -> Advanced Options -> I2C ->j Yes
5.	Reboot the Pi: `sudo reboot`
6.	Wait until the Pi is booted, log back in again and open up a terminal. Power up the Arduino and check that the Pi is detecting the I2C device:

```
> sudo i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- 08 -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```

Notice the Arduino is seen on address 8.

Back to the Pi. I open two terminal windows on my desktop, create a directory called `pi` and `cd` both terminals to the directory. In one window I `ssh` into the Pi, and in the second window I set up an `scp` command. Here are the two commands:

```
> ssh pi@192.168.1.165
> scp testservo.py pi@192.168.1.165:/home/pi
```

Next, I open up an editor to the folder and create a file called `testpot.py` (I initially started working with a potentiometer and didn’t get around to renaming the file yet):

```python
from smbus import SMBus
import time
import sys

if (len(sys.argv) != 3):
	print("Error: Not enough arguments")
	exit()

device = int(sys.argv[1])
value = int(sys.argv[2])
print("device " + str(device))
print("value " + str(value))


bus = SMBus(1) # 512M Pi use i2c port 1, 256M Pi use i2c port 0
time.sleep(1)
address = 0x8

if (value < 256):
	bus.write_i2c_block_data(address, device, [value])
else:
	high, low = value >> 4, value & 0x0FF
	print(high)
	print(low)
	bus.write_i2c_block_data(address, device, [high, low])

bus.close()
```

Usage: `python3 testpot.py [device] [value]`  

Example: `python3 testpot.py 1 180`

The first argument is the device, 1 is the servo motor, and 2 is the brushless motor. The servo motor has a value of 0--180. The brushless motor has a value of 1000--2000 where 1500 is stop and 2000 is full throttle forward.

[Video](https://youtu.be/GUiLuG1Drjg)

## Conclusion

I’m ending this episode with a Pi Zero, Arduino Micro, 5v Voltage Regulator, ESC connected to a brushless motor, and a servo motor. Because of the Pi communicating with the Arduino, I also need a logic level converter. I’m not going to provide links to the parts because I’m not 100% sure I like what I have (for example, the brushless DC motor does not go in reverse). I have spent a couple days trying to figure out why with no success.

I was reluctant to add an Arduino, but once I realized it was necessary to add a microcontroller that could produce a clean PWM signal for the brushless motor, the only decision was which microcontroller. There are a lot of microcontrollers out there, but I decided to use an Arduino Micro because it will do the job; it's small and doesn’t pull a lot of power. The other choices the Arduino Pro Mini and a Teensy. The Arduino Pro Mini comes in a 3.3v variant that would have made life a lot simpler because it operates at the same voltage as the Pi, so a line level converter would not be needed. However, the Pro Min in the 5v and 3.3v is not fast enough. The Teensy is even faster than the Arduino Micro, and the cost is perfect at around $20 but I have more experience with the Arduino Micro, so I went with that. I will consider switching to a Teensy before I finalize the project.

Now, I’ve worked with ESCs before. They are pretty easy to work with, but the directions need to specify a few things that my directions did not. That’s what you get for trying to use a low budget ESP and Motor. At this point, I actually did a search and went page by page reading and trying each and every thing on every page --- including the comments --- until I ran across the fact that ESCs for cars and multicopters are different. Airplane and most multicopter ESCs --- which is what I’ve used --- use 1000 for stop and 2000 for full throttle. Some of these also have reverse so that the vehicle can fly inverted. Car and boat ESC's use 1000 for full reverse, 1500 as stop and 2000 for full forward.

It’s at this point that I would show you a wiring diagram, but since things went haywire (no pun indented), I will just list the connections I made and a photo:

* Arduino Micro VCC -> 5v Voltage Regulator +
* Arduino Micro GND -> 5v Voltage Regulator +
* Arduino Micro 2-> Level Converter HV1
* Arduino Micro 3-> Level Converter HV2
* Arduino Micro 10 -> Servo data (white wire)
* Arduino Micro 11 -> ESC data (white wire)
* Arduino Micro A0 -> Potentiometer wipe (center wire)

---

* Pi SDA -> Level Converter LV1
* Pi SCL -> Level Converter LV2
* Pi 3.3v -> Level Converter HV

---

* Level Converter GND (both of them) -> Common ground
* Level Converter HV -> 5v Voltage Regulator

---

* 5v Voltage Regulator VIN -> 12v Power Supply +
* 5v Voltage Regulator GND -> 12v Power Supply –
* 5v Voltage Regulator VCC -> Micro USB for Pi, Arduino Micro VCC
* 5v Voltage Regulator GND -> Micro USB for Pi, Arduino Micro GND


## References

- A little light reading about [I2C on the Pi](https://stackoverflow.com/questions/24812185/python-smbus-write-byte-and-values-greater-than-1-byte-255)
- [Meaning of cmd param in write_i2c_block_data](https://raspberrypi.stackexchange.com/questions/8469/meaning-of-cmd-param-in-write-i2c-block-data)
- [Programming ESC](https://www.instructables.com/ESC-Programming-on-Arduino-Hobbyking-ESC/)
