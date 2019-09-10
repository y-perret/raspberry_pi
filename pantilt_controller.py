import RPi.GPIO as GPIO
from time import sleep

class PanTiltController:

    # Values in % found for the TowerPro SG90 MicroServo's
    min_duty_cycle = 2
    max_duty_cycle = 12

    #Initial values for each angles
    pan_angle = 90
    tilt_angle = 90

    # Initializer / Instance Attributes
    def __init__(self, pan_pin=3, tilt_pin=5, frequency=50, sleep_time = 0.1, movement_threshold = 0):
        """
        A Pan / Tilt controller is used to control the two servos to create a rotation on two axis
        :param pan_pin: GPIO pin associated to the servo used for panning
        :param tilt_pin: GPIO pin associated to the servo used for tilting
        :param frequency: frequency used by the servos
        :param sleep_time: time between each movement
        :param movement_threshold: threshold in degree of the difference of angles to allow a movement. This reduces small unwanted movements
        """
        self.pan_pin = pan_pin
        self.tilt_pin = tilt_pin
        self.frequency = frequency
        self.sleep_time = sleep_time
        self.movement_threshold = movement_threshold

        #Sets the pin names to board mode
        GPIO.setmode(GPIO.BOARD)

        #Setup the outputs and initialize two "Pulse Width Modulation" (PWN) for the two servos
        GPIO.setup(self.pan_pin, GPIO.OUT)
        GPIO.setup(self.tilt_pin, GPIO.OUT)
        self.pwm1 = GPIO.PWM(self.pan_pin, self.frequency)
        self.pwm2 = GPIO.PWM(self.tilt_pin, self.frequency)

        self.enable = True

    def start(self):
        """
        Start the two PWMs
        """
        self.pwm1.start(0)
        self.pwm2.start(0)

    def pan(self, angle):
        """
        Pan the camera to specific angle
        :param angle: angle range is [0;180]
        """
        #Clamp between 0 and 180
        angle = max(0, min(angle, 180))
        # Move only if the difference is significant
        if abs(angle - self.pan_angle) > self.movement_threshold:
            print("pan: " + str(angle))
            # Compute the duty cycle in % corresponding to the angle
            duty_cycle = angle * (self.max_duty_cycle - self.min_duty_cycle) / 180 + self.min_duty_cycle
            self.pwm1.ChangeDutyCycle(duty_cycle)
            sleep(self.sleep_time)
            #Reduce the wobble between movements
            self.pwm1.ChangeDutyCycle(0)
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
            print("tilt: " + str(angle))
            #Compute the duty cycle in % corresponding to the angle
            duty_cycle = angle * (self.max_duty_cycle - self.min_duty_cycle) / 180 + self.min_duty_cycle
            self.pwm2.ChangeDutyCycle(duty_cycle)
            sleep(self.sleep_time)
            #Reduce the wobble between movements
            self.pwm2.ChangeDutyCycle(0)
            self.tilt_angle = angle

    def stop(self):
        """
        Stop the PWMs and clean the IOs
        """
        self.pan(90)
        self.tilt(90)
        self.pwm1.stop()
        self.pwm2.stop()
        GPIO.cleanup()
        self.enable = False



