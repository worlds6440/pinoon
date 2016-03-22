from triangula.input import SixAxis, SixAxisResource


# Button handler, will be bound to the square button later
def handler(button):
    print('Button {} pressed'.format(button))

# Keep trying to connect the PS3 Controller
while True:
    try:
        # Get a joystick, this will fail unless the SixAxis controller
        # is paired and active. The bind_defaults argument specifies
        # that we should bind actions to the SELECT and START buttons to
        # centre the controller and reset the calibration respectively.
        with SixAxisResource.SixAxisResource(bind_defaults=True) as joystick:
            # Register a button handler for the square button
            joystick.register_button_handler(handler, SixAxis.BUTTON_SQUARE)
            while joystick.is_connected():
                # Read the x and y axes of the left hand stick,
                # the right hand stick has axes 2 and 3
                left_x = joystick.axes[0].corrected_value()
                left_y = joystick.axes[1].corrected_value()
                right_x = joystick.axes[2].corrected_value()
                right_y = joystick.axes[3].corrected_value()
                print("[" + str(left_x) + "," + str(left_y) + "]            [" + str(right_x) + "," + str(right_y) + "]")
    except(IOError):
        print("Controller Not Connected")
