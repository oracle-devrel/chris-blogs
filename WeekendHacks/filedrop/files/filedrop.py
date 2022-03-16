# Python 3 file drop example
# Run: python3 server.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import os
import argparse

parser = argparse.ArgumentParser(description="File drop.")
parser.add_argument("ip", type=str)
parser.add_argument("port", type=int, default=2022)
parser.add_argument("filename", type=str)
parser.add_argument("droppath", type=string)
parser.add_argument("dropname", type=string)
parser.add_argument("dropvalue", type=string)
args = parser.parse_args()

address = (args.ip, args.port)
filename = args.filename
droppath = args.droppath
dropname = args.dropname
dropvalue = args.dropvalue

print("IP=" + args.ip)
print("Port=" + str(args.port))
if os.path.exists(filename):
  print("Filename=" + filename)
print("Path=" + droppath)
print("Name=" + dropname)
print("Value=" + dropvalue)

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/octet-stream")
        self.send_header("Content-Disposition", "attachment; filename=" + filename)
        self.end_headers()

        path = self.path
        name = ""
        value = ""

        if '?' in path:
          path, args = path.split('?', 1)
          name, value = args.split('=', 1)

          if path == "/" + droppath + "/" + filename and name == dropname and value == dropvalue:
            fo = open(filename, "rb")
            self.wfile.write(fo.read())
            fo.close()
            print("success")

        os.remove(filename)

        print(path, name, value)
        return

if __name__ == "__main__":
    webServer = HTTPServer(address, MyServer)
    print("Server started http://%s:%s" % address)

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
