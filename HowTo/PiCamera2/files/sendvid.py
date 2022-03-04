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
