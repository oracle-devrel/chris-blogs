# Stream a Pi Camera to Oracle Cloud Part Deux

by Chris Bensen

![](images/pexels-photography-maghradze-ph-3764958.jpg)
Photo by Photography Maghradze PH from Pexels

If you prefer you can read this blog post on Medium [here](https://chrisbensen.medium.com/stream-a-pi-camera-to-oracle-cloud-part-ii-7ded4258b117).

Last time in [Stream a Pi Camera to Oracle Cloud](https://chrisbensen.medium.com/stream-a-pi-camera-to-oracle-cloud-6328653c60af) part one, I showed you how to stream to Oracle Cloud from a Raspberry Pi with a V2 Pi Camera using the new Pi Camera system. That article was simplified with step-by-step directions. I also explained a lot of the problems the Pi camera system faces, as there are many issues and I haven't seen them outlined in one place. Lastly, when we add up all of these permutations in software, hardware, operating systems, and bugs it becomes very complicated. What I hope you come away with after this series are some examples that have been tested and verified to work so you can use them for your own projects.

Let's look at the Legacy Pi Camera. It's legacy, but it still works (for now). But it's important that I explain some differences at the time of writing this:

- The Legacy Camera currently (Buster and Bullseye) works on Pi Zero, Pi 3 and Pi 4.
- I have not tested the Pi Zero (yet).
- It is not possible to initiate a stream from the Pi to an external server with the New Camera System.
- The New Camera System is not accessible from Python or OpenCV (yet).
- I have not tested every permutation or combination on all Pi.
- I have had better luck with Motion-JPEG when streaming throughout the entire stack (Pi -> Web Server -> Web Browser).
- In a future article I hope to have a full stack H264 example.

# Documentation

These are the best camera docs I have been able to find:
- [Latest Pi Camera Docs](https://buildmedia.readthedocs.org/media/pdf/picamera/latest/picamera.pdf)
- [Camera API](https://picamera.readthedocs.io/en/release-1.10/api_camera.html)
- [Streaming Motion-JPEG](https://www.codeinsideout.com/blog/pi/stream-picamera-mjpeg/)

## Prerequisites

1. You have an OCI account or a [Free Tier Account](https://medium.com/oracledevs/create-an-oracle-always-free-cloud-account-bc6aa82c1397).

1. You have created a [Compute Instance](https://chrisbensen.medium.com/create-an-oci-compute-instance-493d10e2e6a6).

1. You have [locked down ssh](https://chrisbensen.medium.com/white-list-your-ip-address-to-security-connect-to-an-oci-compute-instance-4fb99958f0d9) on your compute to only your computer.

1. You have setup a [Compute instance to be a web server](https://medium.com/@chrisbensen/create-a-simple-python-web-server-on-oci-1d3634a1d7c2).

Find out more about [Compute](https://docs.oracle.com/en-us/iaas/Content/Compute/home.htm?source=:ex:tb:::::RC_WWMK220210P00062:Medium_CBensen&SC=:ex:tb:::::RC_WWMK220210P00062:Medium_CBensen&pcode=WWMK220210P00062) and other [Oracle Cloud documentation](https://docs.oracle.com/en-us/iaas/Content/GSG/Concepts/baremetalintro.htm?source=:ex:tb:::::RC_WWMK220210P00062:Medium_CBensen&SC=:ex:tb:::::RC_WWMK220210P00062:Medium_CBensen&pcode=WWMK220210P00062) [here](https://docs.oracle.com/en-us/iaas/Content/GSG/Concepts/baremetalintro.htm?source=:ex:tb:::::RC_WWMK220210P00062:Medium_CBensen&SC=:ex:tb:::::RC_WWMK220210P00062:Medium_CBensen&pcode=WWMK220210P00062). For interactive support and community check out Oracle's public [Slack channel](https://oracledevrel.slack.com/join/shared_invite/zt-uffjmwh3-ksmv2ii9YxSkc6IpbokL1g#/shared-invite/email) for developers.


# Example Streaming a Pi Camera to Oracle Cloud and Serving that from a Web Server

One of the few examples on the internet that I could find that actually works is this [example](http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming). It hosts a web server on the Pi, just go to the web server on any computer on your network and you can see what the camera sees. I took that example and teased it apart into two pieces: a Python app that runs on the Pi and streams the video from the camera to an IP address. The server receives the stream and hosts a web server. Since the web server is hosted on Oracle Cloud you have a public IP address so anywhere in the world you can see your Pi camera!

To get started you need the prerequisites above.

Note that this example is just an example. It does not handle all error cases or reconnection cases. Once the server or client is terminated both must be restarted. This is unfortunate but by not adding all of the code you get to see the core code required to get this working.

# Cloud Setup

1. Follow the steps [here](https://medium.com/@chrisbensen/create-a-simple-python-web-server-on-oci-1d3634a1d7c2) for adding port 8100 to the security list:

1. Then run the following commands to open up port 8100:

  ```
  sudo firewall-cmd --permanent --zone=public --add-port=8100/tcp
  sudo firewall-cmd --permanent --zone=public --add-port=8100/udp
  sudo firewall-cmd --reload
  ```

1. Copy ``vidserver.py`` to your Compute instance:

    ```
    scp vidserver.py pi@<PI IP Address>:/home/pi
    ```

1. Run the video web server:

    ```
    sudo python3 vidserver.py
    ```

The web server will wait until the stream is connected.

[camserver.py](files/vidserver.py)

```
import logging
import socketserver
from http import server
import socket
import struct

PAGE="""\
<html>
<head>
<title>Raspberry Pi - Surveillance Camera</title>
</head>
<body>
<center><h1>Raspberry Pi - Surveillance Camera</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(("", 8100))
serverSocket.listen()

(clientConnected, clientAddress) = serverSocket.accept()
print("Accepted a connection request from %s:%s"%(clientAddress[0], clientAddress[1]))

def receiveMessage(connection):
    result = None
    # Message: [4 byte message length][variable message]
    lengthOfStruct = internalReceiveMessage(connection, 4)

    if lengthOfStruct:
        messageLength = struct.unpack('>I', lengthOfStruct)[0]
        result = internalReceiveMessage(connection, messageLength)

    return result

def internalReceiveMessage(connection, length):
    # Internal function to receive a specific length number of bytes.
    # Returns the received data or returns None if EOF is encountered.
    result = bytearray()

    while len(result) < length:
        packet = connection.recv(length - len(result))

        if not packet:
            result = None
            break

        result.extend(packet)

    return result

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    frame = receiveMessage(clientConnected)
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
    print("starting")
finally:
    print("shutdown"))
```

## Rasbperry Pi Set Up

1. Set up an SD card with your favorite OS. Here's how you can [install Oracle Linux](https://geraldonit.com/2019/03/18/how-to-install-oracle-linux-on-raspberry-pi/) but Raspberry Pi OS is super easy to install with the [Raspberry Pi Imager](https://www.raspberrypi.com/software/). Whichever OS you decide to use, they will all work and there are reasons to use each one.

  Note that there are some differences between the OS choices and the version of your Raspberry Pi, where some things work and some won't. I'll do my best to note where this is the case, but I don't have an all-inclusive list. Below is a list I've compiled to help clear up the choices.

1. The first thing I do when I boot up a Pi is rename one audio file. When the Pi first boots up you will get an annoying "to install a screen reader press control alt space" if you have audio hooked up:

  ```
  sudo mv /usr/share/piwiz/srprompt.wav /usr/share/piwiz/srprompt.wav.old
  ```

1. Update the OS:

  ```
  sudo apt-get update -y && sudo apt-get upgrade -y
  ```

1. Turn on SPI, I2C and the Legacy Camera:

  ```
  sudo raspi-config
  ```

  **NOTE**: Bullseye does not have this option in the GUI version of the raspi-config tool.

1. Reboot for all changes to take effect:

  ```
  sudo reboot
  ```

1. Setup the camera for Motion-MPEG. Run the command:

  ```
  sudo pico /boot/config.txt
  ```

  At the bottom of the file make sure any line with the name: ``dtoverlay=`` is removed.

  **NOTE**: I have seen examples where ``dtoverlay=imx219`` needs to be in the config.txt but from my experiments this is not the case. I did these tests with the V2 camera.

1. Copy sendvid.py to your Pi:

    ```
    scp sendvid.py pi@<PI IP Address>:/home/pi
    ```

    [sendvid.py](files/sendvid.py)
    ```
    import io
    import picamera
    import socket
    from threading import Condition
    import argparse
    import time
    import struct

    parser = argparse.ArgumentParser(description="stream video.")
    parser.add_argument("ip", type=str)
    parser.add_argument("port", type=int)
    args = parser.parse_args()

    address = (args.ip, args.port)
    clientSocket = None

    while True:
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect(address)
        break
    except socket.error:
        print("Connection Failed, Retrying..")
        time.sleep(1)

    print("connected")


    def sendMessage(connection, message):
    # Message: [4 byte message length][variable message]
    lmessage = struct.pack('>I', len(message)) + message
    connection.sendall(lmessage)

    class StreamingOutput(object):
    def __init__(self):
        self.buffer = io.BytesIO()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            sendMessage(clientSocket, self.buffer.getvalue())
            self.buffer.seek(0)
        return self.buffer.write(buf)

    with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    print("camera")

    try:
        camera.wait_recording(6)
        print("done")
    finally:
        camera.stop_recording()
        clientSocket.close()
    ```

1. Once you have ``sendvid.py`` on your Pi, run it:

    ```
    sudo python3 sendvid.py <IpAddress> 8100
    ```

# View the Video

1. Open up a web browser, type in your public IP address and watch your camera!

If you have any questions or for interactive support and community check out Oracle's public [Slack channel](https://oracledevrel.slack.com/join/shared_invite/zt-uffjmwh3-ksmv2ii9YxSkc6IpbokL1g#/shared-invite/email) for developers.
