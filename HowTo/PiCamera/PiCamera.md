# Stream a Pi Camera to Oracle Cloud

by Chris chrisbensen

If you prefer you can read this blog post on GitHub [here](TODO).

![](images/pexels-haydan-assoendawy-3136711.jpg)
Photo by Haydan As-soendawy from Pexels

A lot of people install security cameras with varying degrees of success. I'll be honest I have bought a few different doorbell cameras as well as bullet cameras and have been very disappointed. The hardware is usually pretty good, but the software and subscriptions leave a lot to be desired. I don't trust any IoT devices on my home network so I run a separate IoT network which can cause additional problems. And unless the camera runs on batteries I'll be running a wire. Usually the wire is for USB 5v power. But if I'm going to run a wire anyway, it might as well be a CAT6 ethernet cable providing power and network to the camera. I know I'm not the only one because many people I've spoken to have similar concerns. Most cameras are powered off USB and use wifi for data. I personally would like no wifi, one cable that provides power and data. This is the first article in a series of articles around streaming video to Oracle Cloud to maybe provide a solution to some of these problems. Because cameras are proprietary, we need a camera that is 100% open source so I figured we should use a Raspberry Pi + a Pi Camera module.

## Prerequisites

1. You have an OCI account or a [Free Tier Account](https://medium.com/oracledevs/create-an-oracle-always-free-cloud-account-bc6aa82c1397).

1. You have created a [Compute Instance](https://chrisbensen.medium.com/create-an-oci-compute-instance-493d10e2e6a6).

1. You have [locked down ssh](https://chrisbensen.medium.com/white-list-your-ip-address-to-security-connect-to-an-oci-compute-instance-4fb99958f0d9) on your compute to only your computer.

## Optional Prerequisites

1. Optional but good for testing; Followed along with Tim's article [Cloud Camera — Simulating a Source](https://medium.com/oracledevs/cloud-camera-simulating-a-source-4e710299606a) to have a live feed rather than a simulated source.

1. Part of the long term [Cloud Camera — Replicating a video stream](https://medium.com/oracledevs/cloud-camera-replicating-a-video-stream-9ec6f9e81c79).

Find out more about [Compute](https://docs.oracle.com/en-us/iaas/Content/Compute/home.htm?source=:so:bl:or:awr:odv:::RC_WWMK220120P00034:&SC=:so:bl:or:awr:odv:::RC_WWMK220120P00034:&pcode=WWMK220120P00034) and other [Oracle Cloud documentation](https://docs.oracle.com/en-us/iaas/Content/GSG/Concepts/baremetalintro.htm?source=:so:bl:or:awr:odv:::RC_WWMK220120P00034:&SC=:so:bl:or:awr:odv:::RC_WWMK220120P00034:&pcode=WWMK220120P00034) [here](https://docs.oracle.com/en-us/iaas/Content/GSG/Concepts/baremetalintro.htm?source=:so:bl:or:awr:odv:::RC_WWMK220120P00034:&SC=:so:bl:or:awr:odv:::RC_WWMK220120P00034:&pcode=WWMK220120P00034). For interactive support and community check out Oracle's public [Slack channel](https://oracledevrel.slack.com/join/shared_invite/zt-uffjmwh3-ksmv2ii9YxSkc6IpbokL1g#/shared-invite/email) for developers.

## Setup a Rasbperry Pi

1. Setup an SD card with your favorite OS. Here's how you can [install Oracle Linux](https://geraldonit.com/2019/03/18/how-to-install-oracle-linux-on-raspberry-pi/) but Raspberry Pi OS is super easy to install with the [Raspberry Pi Imager](https://www.raspberrypi.com/software/). Whichever OS you decided to use they will all work and there are reasons to use each one.

## Setup a Rasbperry Pi for Camera Streaming

Now that you have an SD card with an OS let's set it up to start streaming some video to [Oracle Cloud](https://docs.oracle.com/en-us/iaas/Content/GSG/Concepts/baremetalintro.htm?source=:so:bl:or:awr:odv:::RC_WWMK220120P00034:&SC=:so:bl:or:awr:odv:::RC_WWMK220120P00034:&pcode=WWMK220120P00034). These are the video formats that are supported:

```
v4l2-ctl --list-formats-ext
```

We are going to use the two formats H.264 and Motion-JPEG. Both have their advantages, for now we will use H.264 but we we want to support both. So let's get some streaming setup.

1. The first thing I do when I boot up a Pi is rename one audio file. When the Pi first boots up you will get an annoying "to install a screen reader press control alt space" if you have audio hooked up:

  ```
  sudo mv /usr/share/piwiz/srprompt.wav /usr/share/piwiz/srprompt.wav.old
  ```

1. Update the OS:
  ```
  sudo apt-get update -y && sudo apt-get upgrade -y
  ```

1. Setup the camera. Run the command:
  ```
  sudo pico /boot/config.txt
  ```

  At the bottom of the file change the line:
  ```
  [pi4]
  dtoverlay=vc4-fkms-v3d
  ```

  to:
  ```
  [pi4]
  #dtoverlay=vc4-fkms-v3d
  dtoverlay=imx219
  ```

1. Turn on Legacy Camera, SPI and I2C:
  ```
  sudo raspi-config
  ```

1. Reboot for all changes to take effect:
  ```
  sudo reboot
  ```

1. Use built in tools to stream:
  ```
  libcamera-vid -t 0 --inline -o udp://<IpAddress>:<Port>
  ```

## Camera Streaming Python Script

Built in tools are fine but eventually we will want more control.

1. Let's write a little program so we have complete control:

  stream.py
  ```
  import io
  import picamera
  import socket

  address = ("<IpAddress>", <Port>)

  class H264Streamer():
      def write(self, frame_data):
          package_size = 1472
          size = len(frame_data)
          num_is = int(size / package_size)

          if size % 1472 > 0:
              num_is = num_is + 1

          for i in range(num_is):
              txSock.sendto(frame_data[i * package_size: (i+1) * package_size], address)

  txSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
      output = H264Streamer()
      camera.start_recording(output, format="h264")
      camera.wait_recording(60)
      camera.stop_recording()
  ```

1. Run the script:
  ```
  python3 stream.py
  ```

1. At this point you can run VLC on your local machine and stream there, or you can follow the directions in Tim's article in the optional prerequisites above to setup Oracle Cloud to receive the stream.
