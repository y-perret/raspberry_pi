#!/usr/bin/env python

"""
xbox_controller.py: Executable script used to control the pan/tilt servos with a XBOX 360 controller.
'inputs' packages by 'zeth' is used to handle gamepad inputs: see https://pypi.org/project/inputs/
"""

import threading

from inputs import get_gamepad

from pantilt_controller import PanTiltController


def scale(n):
    """
    Scale the values of the thumbsticks in the range of [0;180] to match the angles
    The values for thumbsticks are initially in the range of [-32768;32767]
    :param n:
    """
    return int((n + 32768.0) * (180.0 - 0.0) / (32767.0 + 32768.0))

def pan(ptc):
    """
    Threading method to pan
    """
    while ptc.enable:
        ptc.pan(pan_angle)

def tilt(ptc):
    """
    Threading method to tilt
    """
    while ptc.enable:
        ptc.tilt(tilt_angle)


#Angles values used for pan/tilt
global pan_angle
pan_angle = 90
global tilt_angle
tilt_angle = 90

ptc = PanTiltController()

# One thread for each of the rotation
thread1 = threading.Thread(target = pan, args = (ptc,))
thread2 = threading.Thread(target = tilt, args = (ptc,))
thread1.setDaemon(True)
thread2.setDaemon(True)
thread1.start()
thread2.start()

try:
    while True:
        #Get events from the gamepad using inputs
        events = get_gamepad()
        for event in events:
            #print(event.ev_type, event.code, event.state)
            #Start button to stop
            if event.code == "BTN_START":
                raise(KeyboardInterrupt)

            #Get joystick values to updates the angles
            if event.code == "ABS_X":
                pan_angle = 180 - scale(event.state)
            if event.code == "ABS_Y":
                tilt_angle = scale(event.state)

except KeyboardInterrupt:
    print("W: interrupt received, stopping...")
finally:
    ptc.stop()
