# Stream a Pi Camera to Oracle Cloud

by Chris Bensen

If you prefer you can read this blog post on Medium [here](https://chrisbensen.medium.com/stream-a-pi-camera-to-oracle-cloud-6328653c60af).

![](images/pexels-haydan-assoendawy-3136711.jpg)
Photo by Haydan As-soendawy from Pexels

A lot of people install security cameras with varying degrees of success. I'll be honest I have bought a few different doorbell cameras as well as bullet cameras and have been very disappointed. The hardware is usually pretty good, but the software and subscriptions leave a lot to be desired. I don't trust any IoT devices on my home network so I run a separate IoT network which can cause additional problems. And unless the camera runs on batteries I'll be running a wire. Usually the wire is for USB 5v power. But if I'm going to run a wire anyway, it might as well be a CAT6 ethernet cable providing power and network to the camera. I know I'm not the only one because many people I've spoken to have similar concerns. Most cameras are powered off USB and use wifi for data. I personally would like no wifi, one cable that provides power and data. This is the first article in a series of articles around streaming video to Oracle Cloud to maybe provide a solution to some of these problems. Because cameras are proprietary, we need a camera that is 100% open source so I figured we should use a Raspberry Pi + a Pi Camera module.

## [](https://github.com/chrisbensen/chris-blogs/blob/main/HowTo/PiCamera/PiCamera.md#prerequisites)Prerequisites

 1. You have an OCI account or a [Free Tier Account](https://medium.com/oracledevs/create-an-oracle-always-free-cloud-account-bc6aa82c1397).

 1. You have created a [Compute Instance](https://chrisbensen.medium.com/create-an-oci-compute-instance-493d10e2e6a6).

 1. You have [locked down ssh](https://chrisbensen.medium.com/white-list-your-ip-address-to-security-connect-to-an-oci-compute-instance-4fb99958f0d9) on your compute to only your computer.

## [](https://github.com/chrisbensen/chris-blogs/blob/main/HowTo/PiCamera/PiCamera.md#optional-prerequisites)Optional Prerequisites

 1. Optional but good for testing; Followed along with Tim's article [Cloud Camera — Simulating a Source](https://medium.com/oracledevs/cloud-camera-simulating-a-source-4e710299606a) to have a live feed rather than a simulated source.

 1. Part of the long term [Cloud Camera — Replicating a video stream](https://medium.com/oracledevs/cloud-camera-replicating-a-video-stream-9ec6f9e81c79).

Find out more about [Compute](https://docs.oracle.com/en-us/iaas/Content/Compute/home.htm?source=:so:bl:or:awr:odv:::RC_WWMK220120P00034:&SC=:so:bl:or:awr:odv:::RC_WWMK220120P00034:&pcode=WWMK220120P00034) and other [Oracle Cloud documentation](https://docs.oracle.com/en-us/iaas/Content/GSG/Concepts/baremetalintro.htm?source=:so:bl:or:awr:odv:::RC_WWMK220120P00034:&SC=:so:bl:or:awr:odv:::RC_WWMK220120P00034:&pcode=WWMK220120P00034) [here](https://docs.oracle.com/en-us/iaas/Content/GSG/Concepts/baremetalintro.htm?source=:so:bl:or:awr:odv:::RC_WWMK220120P00034:&SC=:so:bl:or:awr:odv:::RC_WWMK220120P00034:&pcode=WWMK220120P00034). For interactive support and community check out Oracle's public [Slack channel](https://oracledevrel.slack.com/join/shared_invite/zt-uffjmwh3-ksmv2ii9YxSkc6IpbokL1g#/shared-invite/email) for developers.

## [](https://github.com/chrisbensen/chris-blogs/blob/main/HowTo/PiCamera/PiCamera.md#setup-a-rasbperry-pi)Setup a Rasbperry Pi

1. Set up an SD card with your favorite OS. Here's how you can [install Oracle Linux](https://geraldonit.com/2019/03/18/how-to-install-oracle-linux-on-raspberry-pi/) but Raspberry Pi OS is super easy to install with the [Raspberry Pi Imager](https://www.raspberrypi.com/software/). Whichever OS you decide to use, they will all work and there are reasons to use each one.

  Note that there are some differences between the OS choices and the version of your Raspberry Pi, where some things work and some won't. I'll do my best to note where this is the case, but I don't have an all-inclusive list. Below is a list I've compiled to help clear up the choices.

## [](https://github.com/chrisbensen/chris-blogs/blob/main/HowTo/PiCamera/PiCamera.md#knowlege)Knowlege

***Bullseye***: This is the latest Raspberry Pi OS.
***Buster***:  This is the previous Raspberry Pi OS.

By default the Pi is setup to use the legacy camera stack. This gets complicated real fast so I'll make it as easy as possible.

  The Raspberry Pi kernel tree contains a number of Device Tree Overlays in the arch/arm/boot/dts/overlays folder.
  Each overlay is stored in .dts file and gets compiled into a .dtbo file.
  A .dtbo can be loaded from the config.txt file format:
    ```
    dtoverlay=overlay-name,overlay-arguments
    ```
  ``dtoverlay=vc4-fkms-v3d`` is for display driver even on Pi 4 despite the docs saying it is only for Pi 3.
  ``dtoverlay=imx219`` is for V2 camera but only works with Bullseye.
  Bullseye and Buster support H.264.
  Bullseye and Buster support Motion-MPEG.
  H.264 and Motion-MPEG are not supported at the same time.
  Pi 3 and Pi 4 support H.264.
  Pi Zero, Pi 3 and Pi 4 support and Motion-MPEG.
  This is the best source for [information about the cameras](https://www.raspberrypi.com/documentation/accessories/camera.html) I've found but it is still lacking.

  Please let me know if anything is wrong here so I can update it.

## [](https://github.com/chrisbensen/chris-blogs/blob/main/HowTo/PiCamera/PiCamera.md#setup-a-rasbperry-pi-for-camera-streaming)Setup a Rasbperry Pi for Camera Streaming

Now that you have an SD card with an OS let's set it up to start streaming some video to [Oracle Cloud](https://docs.oracle.com/en-us/iaas/Content/GSG/Concepts/baremetalintro.htm?source=:so:bl:or:awr:odv:::RC_WWMK220120P00034:&SC=:so:bl:or:awr:odv:::RC_WWMK220120P00034:&pcode=WWMK220120P00034). These directions should work with Raspberry Pi OS and Oracle Linux using any Raspberry Pi. These are the video formats that are supported:

```
v4l2-ctl --list-formats-ext
```

There are two video codecs we are interested in; H.264 and Motion-JPEG. Both have their advantages. For example H.264 has less support, it is not supported on Pi Zero because it uses more processor resources, but it uses less network bandwidth. For this article we will use H.264. So let's get some streaming setup.

1. The first thing I do when I boot up a Pi is rename one audio file. When the Pi first boots up you will get an annoying "to install a screen reader press control alt space" if you have audio hooked up:

  ```
  sudo mv /usr/share/piwiz/srprompt.wav /usr/share/piwiz/srprompt.wav.old
  ```

1. Update the OS:
  ```
  sudo apt-get update -y && sudo apt-get upgrade -y
  ```

1. Turn on SPI and I2C:
  ```
  sudo raspi-config
  ```

1. Reboot for all changes to take effect:
  ```
  sudo reboot
  ```

1. Setup the camera for H.264. Run the command:
  ```
  sudo pico /boot/config.txt
  ```

  At the bottom of the file find the line:
  ```
  dtoverlay=vc4-fkms-v3d
  ```

  and add below it:
  ```
  dtoverlay=imx219
  ```

  So now it looks like this:
  ```
  dtoverlay=vc4-fkms-v3d
  dtoverlay=imx219
  ```

  Also make sure you have the following in config.txt:
  ```
  camera_auto_detect=1
  ```

1. Reboot for all changes to take effect:
  ```
  sudo reboot
  ```

1. Use built in tools to stream:
  ```
  libcamera-vid -t 0 --inline -o udp://<IpAddress>:<Port>
  ```

1. At this point you can run VLC on your local machine and stream there, or you can follow the directions in Tim's article in the optional prerequisites above to setup Oracle Cloud to receive the stream. To run VLC locally on a Mac for example run the following:
  ```
  /Applications/VLC.app/Contents/MacOS/VLC udp://@:<Port> :demux=avformat
  ```

There are a few problems with the directions above that I must point out. libcamera-vid will stream h264 (that is the default) which is great, however I don't know how anyone actually has tested this that has not rebuilt the kernel. The packets being sent are jumbo frames and by default the Pi OS is not setup with jumbo frames and there is no easy way to change this. See this artcle by Jeff Geerling [Setting 9000 MTU (Jumbo Frames) on Raspberry Pi OS](https://www.jeffgeerling.com/blog/2020/setting-9000-mtu-jumbo-frames-on-raspberry-pi-os). Jumbo frames will also need to be enabled on the receiving computer.

![](images/vlclinuxsettings.png)

The second problem is VLC on MacOS doesn't work very well. What I have above will work but it will be delayed. By about a 1000ms to be exact. VLC on Linux and Windows however has an option for this. When you go to File | Open Media and choose the Network tab, choose udp://@:<Port>, click the "Show more options" check box at the bottom and change Caching from "1000ms" to "0ms".

There are other options, TCP and the legacy camera system for example. The Pi camera is an amazing piece of hardware and software but things are in a state of change between the legacy camera and the new camera to a point where it is difficult to use. To confuse things there are years of examples using Python2 and the legacy camera system. Hopefully this article helps cut through some of the confusion and future articles will help as well. Stay tuned...
