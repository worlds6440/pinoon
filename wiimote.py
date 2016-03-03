import cwiid
import logging

from numpy import clip, interp


class WiimoteException(Exception):
    pass


class WiimoteNunchukException(WiimoteException):
    pass


class Wiimote():
    """Wrapper class for the wiimote interaction"""
    def __init__(
        self,
        max_tries=5,
        joystick_range=None,
        acc_range=None
    ):
        self.joystick_range = joystick_range if joystick_range else [50, 200]
        self.acc_range = acc_range if acc_range else [50, 200]
        self.wm = None
        attempts = 0

        logging.info("Press 1+2 on your Wiimote now...")

        # Attempt to get a connection to the wiimote
        # try a few times, as it can take a few attempts
        while not self.wm:
            try:
                self.wm = cwiid.Wiimote()
            except RuntimeError:
                if attempts == max_tries:
                    logging.error("cannot create connection")
                    raise WiimoteException(
                        "Could not create connection within {0} tries".format(
                            max_tries
                        )
                    )
                logging.error("Error opening wiimote connection")
                logging.error("attempt {0}".format(attempts))
                attempts += 1

        # set wiimote to report button presses and accelerometer state
        self.wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC | cwiid.RPT_EXT

        # Set led state
        self.wm.led = 1

    def get_state(self):
        """Get the full raw state of the wiimote.
        Returns: dict"""
        return self.wm.state if self.wm else None

    def get_nunchuk_accel_state(self):
        """ Get the nunchuck accelerometer
            Returns a dictionary containing the state of
            the nunchuk joystick in the form:
            {
            "state": {
                    "raw": tuple of the raw joystick readings
                           from cwiid in the form (x, y),
                    "clipped": tuple of the raw values, clipped
                               to the min/max range,
                    "normalised": the 'clipped' tuple, with the
                                values mapped to the range -1 to 1
                }
            "range": The min/max range to clip raw values to
            }
        """
        if 'nunchuk' not in self.get_state():
            logging.debug("state: {0}".format(self.get_state()))
            return None
        else:
            acc_state_raw = self.wm.state['nunchuk']['acc']
            acc_state_clipped = [
                clip(channel, *self.acc_range)
                for channel
                in acc_state_raw
            ]
            acc_state_normalised = [
                interp(channel, self.acc_range, [-1, 1])
                for channel
                in acc_state_raw
            ]
            return dict(
                range=self.acc_range,
                state=dict(
                    raw=acc_state_raw,
                    clipped=acc_state_clipped,
                    normalised=acc_state_normalised
                )
            )

    def get_joystick_state(self):
        """Returns a dictionary containing the state
           of the nunchuk joystick in the form:
            {
            "state": {
                    "raw": tuple of the raw joystick readings
                           from cwiid in the form (x, y),
                    "clipped": tuple of the raw values,
                               clipped to the min/max range,
                    "normalised": the 'clipped' tuple, with
                                  the values mapped to the range -1 to 1
                }
            "range": The min/max range to clip raw values to
            }
        """
        if 'nunchuk' not in self.get_state():
            logging.debug("state: {0}".format(self.get_state()))
            return None
        else:
            joystick_state_raw = self.wm.state['nunchuk']['stick']
            joystick_state_clipped = [
                clip(channel, *self.joystick_range)
                for channel
                in joystick_state_raw
            ]
            joystick_state_normalised = [
                interp(channel, self.joystick_range, [-1, 1])
                for channel
                in joystick_state_raw
            ]
            return dict(
                range=self.joystick_range,
                state=dict(
                    raw=joystick_state_raw,
                    clipped=joystick_state_clipped,
                    normalised=joystick_state_normalised
                )
            )

    def get_buttons(self):
        """Get just the current button state of the wiimote"""
        buttons_state = self.wm.state['buttons']

        return buttons_state

    def get_nunchuk_buttons(self):
        """Get just the current button state of the wiimote nunchuk"""
        if 'nunchuk' not in self.get_state():
            return None
        buttons_state = self.wm.state['nunchuk']['buttons']

        return buttons_state
