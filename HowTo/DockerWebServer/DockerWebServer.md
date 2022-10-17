# Create a Simple Docker Container with a Python Web Server

By Chris Bensen

![](images/pexels-frans-van-heerden-1624695.jpg)
[Photo by Frans van Heerden:](https://www.pexels.com/photo/cargo-containers-trailer-lot-1624695/)

If you prefer you can read this blog post on Medium [here](https://chrisbensen.medium.com/create-a-simple-docker-container-with-a-python-web-server-26534205061a).

If you’re curious about the goings-on of Oracle Developers in their natural habitat, come join us on our [Slack channel](https://bit.ly/devrel_slack) for developers!

This article may seem obvious to some but others need to know how to get started. Having a server running in a container is the beginning of so many great things.

## Prerequisites

1. Install [Docker](https://www.docker.com).

1. Read [Create a Simple Python Web Server](https://medium.com/oracledevs/create-a-simple-python-web-server-on-oci-1d3634a1d7c2) because we will use this Web Server but put it into a Docker container.

## Build a Web Server

1. Create a folder and put all the files we are going to create into that folder.

1. Create **index.html**:
  ```
  <!DOCTYPE html>
  <html>
  <body>
  Hello World
  </body>
  </html>
  ```

1. Create **server.py**:
  ```
  #!/usr/bin/python3
  from http.server import BaseHTTPRequestHandler, HTTPServer
  import time
  import json
  from socketserver import ThreadingMixIn
  import threading

  hostName = "0.0.0.0"
  serverPort = 80

  class Handler(BaseHTTPRequestHandler):
      def do_GET(self):
          # curl http://<ServerIP>/index.html
          if self.path == "/":
              # Respond with the file contents.
              self.send_response(200)
              self.send_header("Content-type", "text/html")
              self.end_headers()
              content = open('index.html', 'rb').read()
              self.wfile.write(content)

          else:
              self.send_response(404)

          return

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
  ```
## Put Everything into a Docker Container

1. Create **Dockerfile**:
  ```
  FROM python:3
  ADD index.html index.html
  ADD server.py server.py
  EXPOSE 8888
  ENTRYPOINT ["python3", "server.py"]
  ```
1. cd into the folder you created.

1. Run ``docker build -f Dockerfile . -t web-server-test``

1. Run ``docker run --rm -p 8000:80 --name web-server-test web-server-test``

There you have it! Enjoy your web server in a Docker container. The nice thing about doing this is as a developer you can run and debug things inside a container just as if they are on your local computer but the only thing that is installed on your local system is Docker.

Next, try creating an Oracle Cloud account [Free Tier](https://medium.com/oracledevs/create-an-oracle-always-free-cloud-account-bc6aa82c1397) and deploy your container there. Who knows, maybe I'll create a How To for that in the future!
