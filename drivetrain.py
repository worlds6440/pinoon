from __future__ import division
import logging
from libs.Adafruit_PWM_Servo_Driver import PWM
from numpy import interp, clip


class DriveTrain():
    """Instantiate a 2WD drivetrain, utilising 2x ESCs,
    controlled using a 2 axis (throttle, steering)
    system"""
    def __init__(
        self,
        pwm_i2c=0x40,
        pwm_freq=50,
        left_channel=0,
        right_channel=1,
        front_channel=2,
        aux_channel1=4,
        aux_channel2=5,
        aux_channel3=6,
        aux_channel4=7,
        debug=False
    ):
        # Main set of motor controller ranges
        self.servo_min = 1000
        self.servo_mid = 1500
        self.servo_max = 2000

        # Full speed range
        self.servo_full_min = 1000
        self.servo_full_max = 2000
        # Low speed range is 1/4 of full speed
        speed_divisor = 2
        self.servo_low_min = int(self.servo_mid - (self.servo_mid-self.servo_full_min) / speed_divisor)
        self.servo_low_max = int(self.servo_mid + (self.servo_full_max-self.servo_mid) / speed_divisor)

        self.channels = {
            'left': left_channel,
            'right': right_channel,
            'front': front_channel,
        }

        self.pwm = PWM(pwm_i2c, debug=debug)
        self.pwm.setPWMFreq(pwm_freq)
        # Flag set to True when motors are allowed to move
        self.drive_enabled = False
        self.disable_drive()

    def set_servo_pulse(self, channel, pulse):
        """Send a raw servo pulse length to a specific speed controller
        channel"""
        # Only send servo pulses if drive is enabled
        if self.drive_enabled:
            # 1,000,000 us per second
            pulseLength = 1000000
            #  60 Hz
            pulseLength /= 50
            # logging.debug("%d us per period" % pulseLength)
            # 12 bits of resolution
            pulseLength /= 4096
            # logging.debug("%d us per bit" % pulseLength)
            # pulse *= 1000
            pulse /= pulseLength
            logging.debug(
                "pulse {0} - channel {1}".format(
                    int(pulse), channel
                )
            )
            self.pwm.setPWM(channel, 0, int(pulse))

    def enable_drive(self):
        """Allow motors to be used"""
        self.drive_enabled = True

    def disable_drive(self):
        """Disable motors so they cant be used"""
        self.set_neutral()
        self.drive_enabled = False

    def set_neutral(self):
        """Send the neutral servo position to both motor controllers"""
        self.set_servo_pulse(self.channels['left'], self.servo_mid)
        self.set_servo_pulse(self.channels['right'], self.servo_mid)
        self.set_servo_pulse(self.channels['front'], self.servo_mid)

    def set_full_speed(self):
        """Set servo range to FULL extents"""
        self.servo_min = self.servo_full_min
        self.servo_max = self.servo_full_max

    def set_low_speed(self):
        """Limit servo range extents"""
        self.servo_min = self.servo_low_min
        self.servo_max = self.servo_low_max

    # TODO - flesh out setters for raw pulse values (both channels)
    def mix_channels_and_assign(self, throttle, steering):
        """Take values for the throttle and steering channels in the range
        -1 to 1, convert into servo pulses, and then mix the channels and
        assign to the left/right motor controllers"""
        if not self.drive_enabled:
            return
        pulse_throttle = self._map_channel_value(throttle)
        pulse_steering = self._map_channel_value(steering)
        output_pulse_left = clip(
            (pulse_throttle + pulse_steering) / 2,
            self.servo_min,
            self.servo_max
        )
        output_pulse_right = clip(
            (pulse_throttle - pulse_steering) / 2 + self.servo_mid,
            self.servo_min,
            self.servo_max
        )

        # Set the servo pulses for left and right channels
        self.set_servo_pulse(self.channels['left'], output_pulse_left)
        self.set_servo_pulse(self.channels['right'], output_pulse_right)

    def mix_channels_omni_and_assign(self, forward, side, rotate):
        """ Take values for throttle, steering and rotation channels
        in the range of -1 to 1, convert to servo pulses, and then mix
        the channels and assign to the left, right and front motors. """
        if not self.drive_enabled:
            return
        pulse_forward = self._map_channel_value(forward) - self.servo_mid
        pulse_side = self._map_channel_value(side) - self.servo_mid
        pulse_rotate = self._map_channel_value(rotate) - self.servo_mid

        # Appears to be RC signal in, we don't need this section
        # VFwd = pulseIn(pin[0], HIGH)-1500
        # VRotate = pulseIn(pin[1], HIGH)-1500
        # VSide =pulseIn(pin[2], HIGH)-1500
        round_dp = 0

        clip_value = (self.servo_max - self.servo_min) / 2.0

        # VFront = constrain(-VSide-VRotate, -500, 500)+1500
        output_pulse_front = clip(
            (-pulse_side-pulse_rotate),
            -clip_value,
            +clip_value
        )
        # VLeft = constrain(-round(VSide*0.15+VFwd*0.86-VRotate),-500,500)+1500
        output_pulse_left = clip(
            -round(
                   pulse_side*0.15+pulse_forward*0.86-pulse_rotate,
                   round_dp
            ),
            -clip_value,
            +clip_value
        )
        # VRight = constrain(round(VSide*0.15-VFwd*0.86-VRotate),-500,500)+1500
        output_pulse_right = clip(
            round(
                  pulse_side*0.15-pulse_forward*0.86-pulse_rotate,
                  round_dp
            ),
            -clip_value,
            +clip_value
        )

        # where pulsein recieves a ~1000-2000 pulse,
        # 1000 = full left/back,
        # 2000 = full right/forward. so Vfwd is +/-500, 0 = stopped.

        # Set the servo pulses for left and right channels
        self.set_servo_pulse(self.channels['left'],
                             output_pulse_left + self.servo_mid)
        self.set_servo_pulse(self.channels['right'],
                             output_pulse_right + self.servo_mid)
        self.set_servo_pulse(self.channels['front'],
                             output_pulse_front + self.servo_mid)

    def _map_channel_value(self, value):
        """Map the supplied value from the range -1 to 1 to a corresponding
        value within the range servo_min to servo_max"""
        return int(
            interp(
                value,
                [-1, 1],
                [self.servo_min, self.servo_max]
            )
        )
