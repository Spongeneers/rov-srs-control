#!/usr/bin/python
# Copyright 2015, Jonathan Lee
# Distributed under the terms of the BSD 3-Clause License
#
#
# ROV_SRS_Main
#
#
# Overview: The main runtime script to handle SRS Control.
#
# Authors:  Jonathan Lee
#

from collections import deque

from Adafruit_BBIO import ADC
from Adafruit_BBIO import GPIO
from Adafruit_BBIO import PWM
import ROV_SRS_Library as SRS

#
# Constant Definitions.
#

# General Program Constants.
PWM_AVG_NUM  = 5        # Pulses to average before saving Commands.
PWM_WID_FREQ = 70.0     # Expected signal frequency [Hz].
PWM_WID_MAX  = 14.1     # Input signal maximum duty cycle [%].
PWM_WID_MIN  = 6.9      # Input signal minimum duty cycle [%].
PWM_WID_TOL  = 25.0     # Tolerance on Pulse Width Deviations [%].

POS_HIST_NUM = 5        # Number of Position Commands to store.

LA_CONTINUOUS = False   # Command Trend check modes.
CS_CONTINUOUS = False
SS_CONTINUOUS = True

# Linear Actuator Hardware Constants.
PIN_LA_IN  =  "P8_8"        # Pin for Input PWM from RC Controller.
PIN_LA_POT =  "P9_37"       # Pin for Input from Potentiometer.
PIN_LA_OUT = ["P8_5",       # Pin for Output to Driver CH1.
              "P8_7"]       # Pin for Output to Driver CH2.

LA_STROKE_TARGET = 1.5      # Target stroke length [inch].

# Carousel Stepper Hardware Constants.
PIN_CS_IN  =  "P8_10"       # Pin for Input PWM from RC Controller.
PIN_CS_OUT = ["P8_13",      # Pin for "DIR" Signal (high/low direction).
              "P8_15"]      # Pin for "STEP" Signal (rising edge).

CS_GRIPPER_NUM = 2          # Number of Grippers on ROV.

# Shoulder Stepper Hardware Constants.
PIN_SS_IN  =  "P8_26"       # Pin for Input PWM from RC Controller.
PIN_SS_OUT = ["P8_17",      # Pin for "DIR" Signal (high/low direction).
              "P8_19"]      # Pin for "STEP" Signal (rising edge).

# Pressure Transducer Hardware Constants.
PIN_PT_IN  = "P9_39"        # Pin for Input from Transducer.
# TODO(Giles): Define Pins

def main():
    """Translates RC Controller Input to appropriate actuator signals.

    This function utilizes a set of initial variable values to setup
    desired functionality parameters (e.g. actuator stroke length), then 
    enters a polling loop to continually check the state of the input 
    signals. Upon proper conditions being met, changes in these inputs 
    cause the program to enter and iterate through one of three state 
    machines (one for each of the actuators on the SRS).

    Args:
        n/A

    Returns:
        N/A
    """
    #
    # Initialize Hardware.
    #
    ADC.setup()

    # Linear Actuator.
    GPIO.setup(PIN_LA_IN, GPIO.IN)
    for __col in range(len(PIN_LA_OUT)):
        GPIO.setup(PIN_LA_OUT[__col], GPIO.OUT)

    # Carousel Stepper.
    GPIO.setup(PIN_CS_IN, GPIO.IN)
    for __col in range(len(PIN_CS_OUT)):
        GPIO.setup(PIN_CS_OUT[__col], GPIO.OUT)

    # Shoulder Stepper.
    GPIO.setup(PIN_SS_IN, GPIO.IN)
    for __col in range(len(PIN_SS_OUT)):
        GPIO.setup(PIN_SS_OUT[__col], GPIO.OUT)

    # Pressure Transducer.
    # TODO(Giles)

    #
    # Initialize Variables.
    #

    # Pulse Width Averages.
    la_avg = 0.0
    cs_avg = 0.0
    ss_avg = 0.0

    # Position Commands.
    la_cmd = 1
    la_cmd_hist = deque(
        (1 for i in range(POS_HIST_NUM)), maxlen = POS_HIST_NUM)
    la_trend = 0

    cs_cmd = 1
    cs_cmd_hist = deque(
        (1 for i in range(POS_HIST_NUM)), maxlen = POS_HIST_NUM)
    cs_trend = 0

    ss_cmd = 1
    ss_cmd_hist = deque(
        (1 for i in range(POS_HIST_NUM)), maxlen = POS_HIST_NUM)
    ss_trend = 0

    #
    # Main program polling loop.
    #
    while True:
        #
        # Linear Actuator polling.
        #

        # Determine Average Pulse Width.
        #la_avg = SRS.get_width(
        #    PIN_LA_IN, PWM_AVG_NUM, PWM_WID_FREQ,
        #    PWM_WID_MAX, PWM_WID_MIN, PWM_WID_TOL)

        # Add new Position Command to History.
        #la_cmd = SRS.set_position(
        #    la_avg,
        #    PWM_WID_FREQ, PWM_WID_MAX, PWM_WID_MIN, PWM_WID_TOL)
        #if la_cmd is 1:
        #    la_cmd = la_cmd_hist[POS_HIST_NUM - 1]
        #la_cmd_hist.append(la_cmd)

        # Check for Position Command Persistance.
        #la_trend = SRS.check_trend(
        #    la_cmd_hist,
        #    LA_CONTINUOUS)

        # Process Position Command.
        #SRS.move_linear(
        #    la_trend,
        #    PIN_LA_OUT, PIN_LA_POT, LA_STROKE_TARGET)

        #
        # Carousel Stepper polling.
        #

        # Determine Average Pulse Width.
        #cs_avg = SRS.get_width(
        #    PIN_CS_IN, PWM_AVG_NUM, PWM_WID_FREQ,
        #    PWM_WID_MAX, PWM_WID_MIN, PWM_WID_TOL)

        # Add new Position Command to History.
        #cs_cmd = SRS.set_position(
        #    cs_avg,
        #    PWM_WID_FREQ, PWM_WID_MAX, PWM_WID_MIN, PWM_WID_TOL)
        #if cs_cmd is 1:
        #    cs_cmd = cs_cmd_hist[POS_HIST_NUM - 1]
        #cs_cmd_hist.append(cs_cmd)

        # Check for Position Command Persistance.
        #cs_trend = SRS.check_trend(
        #    cs_cmd_hist,
        #    CS_CONTINUOUS)

        # Process Position Command.
        #SRS.move_carousel(
        #    cs_trend,
        #    PIN_CS_OUT, CS_GRIPPER_NUM)

        #
        # Shoulder Stepper polling.
        #

        # Determine Average Pulse Width.
        ss_avg = SRS.get_width(
            PIN_SS_IN, PWM_AVG_NUM, PWM_WID_FREQ,
            PWM_WID_MAX, PWM_WID_MIN, PWM_WID_TOL)

        # DEBUG:
        print 'Shoulder Pulse Width: {}'.format(ss_avg)

        # Add new Position Command to History.
        ss_cmd_hist.append(SRS.set_position(
            ss_avg,
            PWM_WID_FREQ, PWM_WID_MAX, PWM_WID_MIN, PWM_WID_TOL))

        # DEBUG:
        print 'Shoulder History: {}'.format(ss_cmd_hist)

        # Check for Position Command Persistance.
        ss_trend = SRS.check_trend(
            ss_cmd_hist,
            SS_CONTINUOUS)

        # DEBUG:
        print 'Shoulder Trend: {}\n'.format(ss_trend)

        # Process Position Command.
        SRS.move_shoulder(
            ss_trend,
            PIN_SS_OUT)

        #
        # Pressure Transducer polling.
        #

        # TODO(Giles)
