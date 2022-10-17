#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
from socketserver import ThreadingMixIn
import threading
import requests

hostName = "0.0.0.0"
serverPort = 80

speed = 0
status = 'green'
gimme = False

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        global status
        global speed
        global gimme

        # curl http://<ServerIP>/index.html
        if self.path == "/":
            print('running server...')

            # Respond with the file contents.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            content = open('index.html', 'rb').read()
            self.wfile.write(content)

        # curl http://<ServerIP>/candy
        elif self.path.upper() == "/candy".upper():
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            body = {'status': status}
            self.wfile.write(bytes(json.dumps(body), "utf8"))
            gimme = True

        # curl http://<ServerIP>/query
        elif self.path.upper() == "/query".upper():
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            body = {'status': status, 'speed': speed}
            self.wfile.write(bytes(json.dumps(body), "utf8"))

        else:
            self.send_response(404)

        return

    def do_POST(self):
        global speed
        global status
        global gimme

        # refuse to receive non-json content
        if self.headers.get('content-type') != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length))

        response = 0
        body = {}

        # curl -X POST -H "Content-Type: application/json" -d '{"speed":5}' http://<ServerIP>/auto
        if self.path.upper() == "/auto".upper():
            response = 200
            body = {'status': 'true'}
            speed = message['speed']
            print(speed)

        # curl -X POST -H "Content-Type: application/json" -d '{"status":"green"}' http://<ServerIP>/whattodo
        elif self.path.upper() == "/whattodo".upper():
            status = message['status']
            response = 200
            body = {'gimme': gimme}
            gimme = False


        self.send_response(response)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(body), "utf8"))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == "__main__":
    webServer = ThreadedHTTPServer((hostName, serverPort), Handler)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
