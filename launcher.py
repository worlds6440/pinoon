#!/usr/bin/env python
""" Main python script to call, waits for robot button
presses to either start wiimote stuff, or shutdown pi """

import RPi.GPIO as GPIO
import time
import os

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def shutdown_callback(channel):
    """ Threaded callback function called
    when user presses a button """
    print("Shutting down pi")
    os.system("sudo shutdown -h now")


# Callback function
GPIO.add_event_detect(
    17,
    GPIO.FALLING,
    callback=shutdown_callback,
    bouncetime=300
)

while (True):
    try:
        time.sleep(1)

    except KeyboardInterrupt:
        GPIO.cleanup()       # clean up GPIO on CTRL+C exit
GPIO.cleanup()           # clean up GPIO on normal exit
