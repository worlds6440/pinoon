from triangula.input import SixAxis, SixAxisResource


# Button handler, will be bound to the square button later
def handler(button):
    print('Button {} pressed'.format(button))


# Get a joystick, this will fail unless the SixAxis controller
# is paired and active. The bind_defaults argument specifies
# that we should bind actions to the SELECT and START buttons to
# centre the controller and reset the calibration respectively.
joystick = SixAxisResource(bind_defaults=True)

# Register a button handler for the square button
joystick.register_button_handler(handler, SixAxis.BUTTON_SQUARE)
while 1:
    # Read the x and y axes of the left hand stick,
    # the right hand stick has axes 2 and 3
    left_x = joystick.axes[0].corrected_value()
    left_y = joystick.axes[1].corrected_value()
    right_x = joystick.axes[2].corrected_value()
    right_y = joystick.axes[3].corrected_value()
    print("[" + str(left_x) + "," + str(left_y) + "][" + str(right_x) + "," + str(right_y) + "]")
