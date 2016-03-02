#!/usr/bin/env python
""" Main python script to call, waits for robot button
presses to either start wiimote stuff, or shutdown pi """

import RPi.GPIO as GPIO
import time
import os
import sys

start_pin = 24
shutdown_pin = 18

# Project installation directory
project_dir = "/home/pi/Projects/pinoon/"
if len(sys.argv) > 1:
    project_dir = sys.argv[1]
# Ensure project path ends in trailing '/'
os.path.join(project_dir, '')

# Change to Doorbell folder
os.chdir(project_dir)

# Pull up appropriate internal resistors
GPIO.setmode(GPIO.BCM)
GPIO.setup(start_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(shutdown_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def shutdown_callback(channel):
    """ Threaded callback function called
    when user presses the shutdown button """
    print("Shutting down pi")
    os.system("sudo shutdown -h now")


def start_wiimote_callback(channel):
    """ Threaded callback function called
    when user presses the start button """
    print("Starting wiimote")


# Callback function
GPIO.add_event_detect(
    shutdown_pin,
    GPIO.FALLING,
    callback=shutdown_callback
)
# Callback function
GPIO.add_event_detect(
    start_pin,
    GPIO.FALLING,
    callback=start_wiimote_callback
)

while (True):
    try:
        time.sleep(1)

    except KeyboardInterrupt:
        GPIO.cleanup()       # clean up GPIO on CTRL+C exit
GPIO.cleanup()           # clean up GPIO on normal exit
