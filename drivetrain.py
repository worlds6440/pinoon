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
        # Low speed range is 1/4 of full speed
        speed_divisor = 2

        # *** MOTOR 1 *** LEFT
        # Full speed range
        self.motor1_servo_mid = 1500
        self.motor1_servo_full_min = 1000
        self.motor1_servo_full_max = 2000
        self.motor1_servo_min = self.motor1_servo_full_min
        self.motor1_servo_max = self.motor1_servo_full_max
        self.motor1_servo_low_min = int(self.motor1_servo_mid - (self.motor1_servo_mid-self.motor1_servo_full_min) / speed_divisor)
        self.motor1_servo_low_max = int(self.motor1_servo_mid + (self.motor1_servo_full_max-self.motor1_servo_mid) / speed_divisor)

        # *** MOTOR 2 *** RIGHT
        # Full speed range
        self.motor2_servo_mid = 1500
        self.motor2_servo_full_min = 1000
        self.motor2_servo_full_max = 2000
        self.motor2_servo_min = self.motor2_servo_full_min
        self.motor2_servo_max = self.motor2_servo_full_max
        self.motor2_servo_low_min = int(self.motor2_servo_mid - (self.motor2_servo_mid-self.motor2_servo_full_min) / speed_divisor)
        self.motor2_servo_low_max = int(self.motor2_servo_mid + (self.motor2_servo_full_max-self.motor2_servo_mid) / speed_divisor)

        # *** MOTOR 3 *** FRONT
        # Full speed range
        self.motor3_servo_mid = 1500
        self.motor3_servo_full_min = 1000
        self.motor3_servo_full_max = 2000
        self.motor3_servo_min = self.motor3_servo_full_min
        self.motor3_servo_max = self.motor3_servo_full_max
        self.motor3_servo_low_min = int(self.motor3_servo_mid - (self.motor3_servo_mid-self.motor3_servo_full_min) / speed_divisor)
        self.motor3_servo_low_max = int(self.motor3_servo_mid + (self.motor3_servo_full_max-self.motor3_servo_mid) / speed_divisor)

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
        self.set_servo_pulse(self.channels['left'], self.motor1_servo_mid)
        self.set_servo_pulse(self.channels['right'], self.motor2_servo_mid)
        self.set_servo_pulse(self.channels['front'], self.motor3_servo_mid)

    def set_full_speed(self):
        """Set servo range to FULL extents"""
        self.motor1_servo_min = self.motor1_servo_full_min
        self.motor1_servo_max = self.motor1_servo_full_max
        self.motor2_servo_min = self.motor2_servo_full_min
        self.motor2_servo_max = self.motor2_servo_full_max
        self.motor3_servo_min = self.motor3_servo_full_min
        self.motor3_servo_max = self.motor3_servo_full_max

    def set_low_speed(self):
        """Limit servo range extents"""
        self.motor1_servo_min = self.motor1_servo_low_min
        self.motor1_servo_max = self.motor1_servo_low_max
        self.motor2_servo_min = self.motor2_servo_low_min
        self.motor2_servo_max = self.motor2_servo_low_max
        self.motor3_servo_min = self.motor3_servo_low_min
        self.motor3_servo_max = self.motor3_servo_low_max

    def mix_channels_omni_and_assign(self, forward, side, rotate):
        """ Take values for throttle, steering and rotation channels
        in the range of -1 to 1, convert to servo pulses, and then mix
        the channels and assign to the left, right and front motors. """
        if not self.drive_enabled:
            return

        # Appears to be RC signal in, we don't need this section
        # VFwd = pulseIn(pin[0], HIGH)-1500
        # VRotate = pulseIn(pin[1], HIGH)-1500
        # VSide =pulseIn(pin[2], HIGH)-1500
        round_dp = 0

        # VFront = constrain(-VSide-VRotate, -500, 500)+1500
        output_front = clip(
            (-float(side)-float(rotate)),
            -1.0,
            +1.0
        )
        # VLeft = constrain(-round(VSide*0.15+VFwd*0.86-VRotate),-500,500)+1500
        output_left = clip(
            -round(
                   float(side)*0.15+float(forward)*0.86-float(rotate),
                   round_dp
            ),
            -1.0,
            +1.0
        )
        # VRight = constrain(round(VSide*0.15-VFwd*0.86-VRotate),-500,500)+1500
        output_right = clip(
            round(
                  float(side)*0.15-float(forward)*0.86-float(rotate),
                  round_dp
            ),
            -1.0,
            +1.0
        )

        # where pulsein recieves a ~1000-2000 pulse,
        # 1000 = full left/back,
        # 2000 = full right/forward. so Vfwd is +/-500, 0 = stopped.

        output_pulse_left = self._map_channel_value(output_left, 1)
        output_pulse_right = self._map_channel_value(output_right, 2)
        output_pulse_front = self._map_channel_value(output_front, 3)

        logging.info("mixing values LRF: {0} : {1} : {2}".format(output_left, output_right, output_front))
        logging.info("mixing pulses LRF: {0} : {1} : {2}".format(output_pulse_left, output_pulse_right, output_pulse_front))

        # Set the servo pulses for left and right channels
        self.set_servo_pulse(self.channels['left'], output_pulse_left)
        self.set_servo_pulse(self.channels['right'], output_pulse_right)
        self.set_servo_pulse(self.channels['front'], output_pulse_front)

    def _map_channel_value(self, value, motor):
        """Map the supplied value from the range -1 to 1 to a corresponding
        value within the range servo_min to servo_max"""
        if motor == 1:
            return int(
                interp(
                    float(value),
                    [-1.0, 1.0],
                    [float(self.motor1_servo_min),
                     float(self.motor1_servo_max)]
                )
            )
        if motor == 2:
            return int(
                interp(
                    float(value),
                    [-1.0, 1.0],
                    [float(self.motor2_servo_min),
                     float(self.motor2_servo_max)]
                )
            )
        if motor == 3:
            return int(
                interp(
                    float(value),
                    [-1.0, 1.0],
                    [float(self.motor3_servo_min),
                     float(self.motor3_servo_max)]
                )
            )
