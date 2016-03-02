#!/usr/bin/env python
""" Main python script to call, waits for robot button
presses to either start wiimote stuff, or shutdown pi """

import RPi.GPIO as GPIO
import time
import os
import sys
import threading
from wiimote import Wiimote, WiimoteException
import drivetrain
import rc

start_pin = 24
shutdown_pin = 18
pwm_address = 0x40

# Thread pointer for RC mode
rc_class = None
rc_thread = None
# class pointers to wiimote and drivetrain
drive = None
wiimote = None

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


def kill_rc_thread():
    """ Stop any active RC thread """
    global rc_class
    global rc_thread
    if rc_class is not None:
        rc_class.stop()
    rc_class = None
    rc_thread = None


def shutdown_callback(channel):
    """ Threaded callback function called
    when user presses the shutdown button """
    print("Shutting down pi")
    os.system("sudo shutdown -h now")


def start_wiimote_callback(channel):
    """ Threaded callback function called
    when user presses the start button """
    global drive
    global wiimote
    global rc_class
    global rc_thread
    if not rc_class:
        print("Starting RC Mode")
        # Create and start a new thread running the remote control script
        rc_class = rc.rc(drive, wiimote)
        rc_thread = threading.Thread(target=rc_class.run)
        rc_thread.start()
    else:
        print("Stopping RC Mode")
        # Kill Thread
        kill_rc_thread()


def set_neutral(drive, wiimote):
    """Simple method to ensure motors are disabled"""
    if drive:
        drive.set_neutral()
        drive.disable_drive()
    if wiimote is not None:
        # turn on leds on wii remote
        wiimote.led = 2


def set_drive(drive, wiimote):
    """Simple method to highlight that motors are enabled"""
    if wiimote is not None:
        # turn on leds on wii remote
        # turn on led to show connected
        drive.enable_drive()
        wiimote.led = 1


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


# Initiate the drivetrain
drive = drivetrain.DriveTrain(pwm_i2c=pwm_address)
# Initiate the wiimote connection
wiimote = None
while not wiimote:
    # Loop for ever waiting for the wiimote to connect.
    try:
        print("Waiting for you to press '1+2' on wiimote")
        wiimote = Wiimote()

    except WiimoteException:
        print("Wiimote error")
        # logging.error("Could not connect to wiimote. please try again")

try:
    # Constantly check wiimote for button presses
    loop_count = 0
    while wiimote:
        buttons_state = wiimote.get_buttons()
        nunchuk_buttons_state = wiimote.get_nunchuk_buttons()
        joystick_state = wiimote.get_joystick_state()

        # Test if B button is pressed
        if (
            joystick_state is None or
            (buttons_state & cwiid.BTN_B) or
            (nunchuk_buttons_state & cwiid.NUNCHUK_BTN_Z)
        ):
            # No nunchuk joystick detected or B or Z button
            # pressed, must go into neutral for safety
            set_neutral(drive, wiimote)
        else:
            # Enable motors
            set_drive(drive, wiimote)

        # MUST have small sleep here, otherwise PWM
        # board gets too many events and crashes.
        time.sleep(0.05)

except (Exception, KeyboardInterrupt) as e:
    print("Ctrl+C Pressed")

# Finally, always close active threads
kill_rc_thread()
# clean up GPIO on normal exit
GPIO.cleanup()
