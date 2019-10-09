#!/usr/bin/env python3

"""
pan_tilt_tracking.py: Script used to track a face with camera fixed on pan/tilt servos
This is a modified version from the tutorial found on
https://www.pyimagesearch.com/2019/04/01/pan-tilt-face-tracking-with-a
-raspberry-pi
-and-opencv/

USAGE
python pan_tilt_tracking.py --cascade haarcascade_frontalface_default.xml
"""




# import necessary packages
from multiprocessing import Manager
from multiprocessing import Process
from imutils.video import VideoStream
from face_detector import FaceDetector
from pantilt_controller import PanTiltController
from pid import PID
import argparse
import signal
import time
import sys
import cv2

# define the range for the motors
servoRange = (0, 180)

# function to handle keyboard interrupt
def signal_handler(sig, frame):
	'''
	Handle the exit of the processes
	:param sig:
	:param frame:
	:return:
	'''

	# print a status message
	print("[INFO] You pressed `ctrl + c`! Exiting...")

	# exit
	sys.exit()

def face_center(args, faceX, faceY, centerX, centerY):
	'''
	Process which continuously search for a face and its center
	:param args: command line arguments dictionary
	:param faceX: x coordinates of face center
	:param faceY: y coordinates of face center
	:param centerX: center of the frame
	:param centerY: center of the frame
	'''

	# signal trap to handle keyboard interrupt
	signal.signal(signal.SIGINT, signal_handler)

	# start the video stream and wait for the camera to warm up
	vs = VideoStream(usePiCamera=True).start()
	time.sleep(2.0)

	# initialize the face detector
	fd = FaceDetector(args["cascade"])

	# loop indefinitely
	while True:
		# grab the frame from the threaded video stream
		frame = vs.read()

		# calculate the center of the frame as this is where we will
		# try to keep the face
		(H, W) = frame.shape[:2]
		centerX.value = W // 2
		centerY.value = H // 2

		# find the face's location
		faceLoc = fd.update(frame, (centerX.value, centerY.value))
		((faceX.value, faceY.value), rect) = faceLoc

		# extract the bounding box and draw it
		if rect is not None:
			(x, y, w, h) = rect
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0),
				2)

		# display the frame to the screen
		cv2.imshow("Pan-Tilt Face Tracking", frame)
		cv2.waitKey(1)

def pid_process(output, p, i, d, faceCoord, centerCoord):
	'''
	Process used to apply a PID on the angle used by the servo
	:param output: The servo angle that is calculated by our PID controller
	:param p: PID constant
	:param i: PID constant
	:param d: PID constant
	:param faceCoord: x or y (depending on pan oir tilt) coordinate of the detected face
	:param centerCoord: center (x or y) of the frame
	'''
	# signal trap to handle keyboard interrupt
	signal.signal(signal.SIGINT, signal_handler)

	# create a PID and initialize it
	p = PID(p.value, i.value, d.value)
	p.initialize()

	# loop indefinitely
	while True:
		# calculate the error
		error = centerCoord.value - faceCoord.value
		#print(error, p.update(error))

		# update the value
		output.value += p.update(error, 0.05)

def in_range(val, start, end):
	# determine the input vale is in the supplied range
	return (val >= start and val <= end)

def set_servos(pan, tlt):
	'''
	Process to hanbdle the pan/tilt of the servos
	:param pan: pan angle
	:param tlt: tilt angle
	'''
	# signal trap to handle keyboard interrupt
	signal.signal(signal.SIGINT, signal_handler)

	# Create a Pan/Tilt Controller
	ptc = PanTiltController(movement_threshold = 0, sleep_time = 0.05)

	time.sleep(0.5)


	# loop indefinitely
	while True:

                
		tiltAngle = 180 - tlt.value -90
		panAngle = pan.value + 90

		#print(panAngle, tiltAngle)

		#Pan and tilt
		ptc.pan_tilt(panAngle, tiltAngle)

# check to see if this is the main body of execution
if __name__ == "__main__":
	# construct the argument parser and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-c", "--cascade", type=str, default="haarcascade_frontalface_default.xml",
		help="path to input Haar cascade for face detection")
	args = vars(ap.parse_args())
	print(args)

	# start a manager for managing process-safe variables
	with Manager() as manager:

		# set integer values for the face center (x, y)-coordinates
		centerX = manager.Value("i", 0)
		centerY = manager.Value("i", 0)

		# set integer values for the face's (x, y)-coordinates
		faceX = manager.Value("i", 0)
		faceY = manager.Value("i", 0)

		# pan and tilt values will be managed by independant PIDs
		pan = manager.Value("i", 0)
		tlt = manager.Value("i", 0)

		# set PID values for panning
		panP = manager.Value("f", 0.02)
		panI = manager.Value("f", 0.005)
		panD = manager.Value("f", 0.002)

		# set PID values for tilting
		tiltP = manager.Value("f", 0.02)
		tiltI = manager.Value("f", 0.005)
		tiltD = manager.Value("f", 0.002)

		# we have 4 independent processes
		# 1. faceCenter  - finds/localizes the face
		# 2. panning       - PID control loop determines panning angle
		# 3. tilting       - PID control loop determines tilting angle
		# 4. setServos     - drives the servos to proper angles based
		#                    on PID feedback to keep face in center
		processFaceCenter = Process(target=face_center,
			args=(args, faceX, faceY, centerX, centerY))
		processPanning = Process(target=pid_process,
			args=(pan, panP, panI, panD, faceX, centerX))
		processTilting = Process(target=pid_process,
			args=(tlt, tiltP, tiltI, tiltD, faceY, centerY))
		processSetServos = Process(target=set_servos, args=(pan, tlt))

		# start all 4 processes
		processFaceCenter.start()
		processPanning.start()
		processTilting.start()
		processSetServos.start()

		# join all 4 processes
		processFaceCenter.join()
		processPanning.join()
		processTilting.join()
		processSetServos.join()

		# disable the servos
		ptc.stop()
