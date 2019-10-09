# Raspberry Pi Personal Project

This is a personal project I worked on during my free time. The idea was to explore possible applications for the Raspberry Pi 4 computer I bought.
The goal of the project is to extend my knowledge in different fields related to the PI (linux, hardware, I/O, image processing,...)

## Material and setup

The material used in this project is:

* Raspberry Pi 4 (4GB RAM)
* The Raspberry Pi Camera Module v2
* [Pan/Tilt Bracket Kit (Single Attachment)](https://www.pi-shop.ch/media/catalog/product/cache/1/image/650x/040ec09b1e35df139433887a97daa66f/1/4/14391-01a.jpg)
* Legos used for support of the camera

![Alt text](images/setup2.jpg?raw=true "Material")

## Prerequisites

Python installed with the following libraries:

```
[OpenCV](https://opencv.org) - Library for face detection
[pigpio](http://abyz.me.uk/rpi/pigpio/) - Library for the Raspberry which allows control of the General Purpose Input Outputs (GPIO)
[inputs](https://pypi.org/project/inputs/) - Inputs aims to provide cross-platform Python support for keyboards, mice and gamepads
```

## Control of pan/tilt servos using a controller

The first feature is the control of the pan/tilt with a controller (XBOX).

```
python xbox_controller.py
```

## Face Tracking

Track a face with the camera and move the the servos to follow it.

```
python pan_tilt_tracking.py
```

## TODO list

Some possible features I plan to add:

* Web interface to control the camera
* Face recognition 
* Object recognition

## Acknowledgments

* Adrian Rosebrock for the tutorial on [pyimagesearch](https://www.pyimagesearch
.com/2019/04/01/pan-tilt-face-tracking-with-a-raspberry-pi-and-opencv/) which has been used as base for face tracking
