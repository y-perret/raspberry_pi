#!/usr/bin/env python

"""
pantilt_controller.py: Class used to controll servos using the pigpio library
"""
from time import sleep
import pigpio
import signal
import sys

class PanTiltController:

    # Values in ms found experimentally for the TowerPro SG90 MicroServo's
    min_pulse_width = 500
    max_pulse_width = 2500

    #Initial values for each angles
    pan_angle = 90
    tilt_angle = 90

    # Initializer / Instance Attributes
    def __init__(self, pan_pin=2, tilt_pin=3, sleep_time = 0.1, movement_threshold = 0):
        """
        A Pan / Tilt controller is used to control the two servos to create a rotation on two axis
        :param pan_pin: GPIO (BCM) pin associated to the servo used for panning
        :param tilt_pin: GPIO (BCM) pin associated to the servo used for tilting
        :param sleep_time: time between each movement
        :param movement_threshold: threshold in degree of the difference of angles to allow a movement. This reduces small unwanted movements
        """
        self.pan_pin = pan_pin
        self.tilt_pin = tilt_pin
        self.sleep_time = sleep_time
        self.movement_threshold = movement_threshold
        self.pi = pigpio.pi() # Connect to local Pi.
        self.enable = True

        # signal trap to handle keyboard interrupt
        signal.signal(signal.SIGINT, self.signal_handler)

        self.pan(self.pan_angle)
        self.tilt(self.tilt_angle)


    def pan(self, angle):
        """
        Pan the camera to specific angle
        :param angle: angle range is [0;180]
        """
        #Clamp between 0 and 180
        angle = max(0, min(angle, 180))
        # Move only if the difference is significant
        if abs(angle - self.pan_angle) > self.movement_threshold:
            # Compute the duty cycle in % corresponding to the angle
            pulse_width = angle * (self.max_pulse_width - self.min_pulse_width) / 180 + self.min_pulse_width
            self.pi.set_servo_pulsewidth(self.pan_pin, pulse_width)
            sleep(self.sleep_time)

            #Store the previous angle
            self.pan_angle = angle

    def tilt(self, angle):
        """
        Tilt the camera to specific angle
        :param angle: angle range is [30;150]
        """
        # Clamp between 30 and 150
        angle = max(30, min(angle, 150))
        # Move only if the difference is significant
        if abs(angle - self.tilt_angle) > self.movement_threshold:
            #Compute the duty cycle in % corresponding to the angle
            pulse_width = angle * (self.max_pulse_width - self.min_pulse_width) / 180 + self.min_pulse_width
            self.pi.set_servo_pulsewidth(self.tilt_pin, pulse_width)
            sleep(self.sleep_time)
            self.tilt_angle = angle

    def pan_tilt(self, pan_a, tilt_a):
        """
        Pan and tilt the two servos with only one sleep for the two independant movcements
        :param pan_a: pan angle range is [0;180]
        :param tilt_a: tilt angle range is [0;180]
        """
        # Clamp between 0 and 180
        angle = max(0, min(pan_a, 180))
        # Move only if the difference is significant
        if abs(angle - self.pan_angle) > self.movement_threshold:
            # Compute the duty cycle in % corresponding to the angle
            pulse_width = angle * (self.max_pulse_width - self.min_pulse_width) / 180 + self.min_pulse_width
            self.pi.set_servo_pulsewidth(self.pan_pin, pulse_width)
            # Store the previous angle
            self.pan_angle = angle

        # Clamp between 30 and 150
        angle = max(30, min(tilt_a, 150))
        # Move only if the difference is significant
        if abs(angle - self.tilt_angle) > self.movement_threshold:
            # Compute the duty cycle in % corresponding to the angle
            pulse_width = angle * (self.max_pulse_width - self.min_pulse_width) / 180 + self.min_pulse_width
            self.pi.set_servo_pulsewidth(self.tilt_pin, pulse_width)
            self.tilt_angle = angle

        sleep(self.sleep_time)

    def stop(self):
        """
        Stop the PWMs and clean the IOs
        """
        self.enable = False
        #Reinitialize positions
        self.pan(90)
        self.tilt(90)
        #Switch off servos
        self.pi.set_servo_pulsewidth(self.pan_pin, 0)
        self.pi.set_servo_pulsewidth(self.tilt_pin, 0)
        self.pi.stop()

    def signal_handler(self, sig, frame):
        '''
        Handle the exit of the processes
        '''

        # print a status message
        print("[INFO] You pressed `ctrl + c`! Exiting...")

        # disable the servos
        self.stop()

        sys.exit(0)



