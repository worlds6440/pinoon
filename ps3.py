from triangula.input import SixAxis, SixAxisResource


# Keep trying to connect the PS3 Controller
while True:
    try:
        # Get a joystick, this will fail unless the SixAxis controller
        # is paired and active. The bind_defaults argument specifies
        # that we should bind actions to the SELECT and START buttons to
        # centre the controller and reset the calibration respectively.
        with SixAxisResource(bind_defaults=True) as joystick:
            while joystick.is_connected():

                # Look for button presses
                buttons_pressed = joystick.get_and_clear_button_press_history()
                if buttons_pressed & 1 << SixAxis.BUTTON_SQUARE:
                    print("Square button pressed")

                # Read the x and y axes of the left hand stick,
                # the right hand stick has axes 2 and 3
                left_x = joystick.axes[0].corrected_value()
                left_y = joystick.axes[1].corrected_value()
                right_x = joystick.axes[2].corrected_value()
                right_y = joystick.axes[3].corrected_value()
                print "[{:10.2f}, {:10.2f}][{:10.2f}, {:10.2f}]".format(left_x, left_y, right_x, right_y)
    except(IOError):
        print("Controller Not Connected")
