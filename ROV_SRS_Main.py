#!/usr/bin/python
# Copyright 2015, Jonathan Lee
# Distributed under the terms of the BSD 3-Clause License
#
#
# ROV_SRS_Main
#
#
# Overview:	The main runtime script to handle SRS Control.
#
# Authors:	Jonathan Lee
#

import Adafruit_BBIO.GPIO as GPIO
import ROV_SRS_Library as SRS

#
# Constant Definitions.
#
# Refer to the "Adafruit_BBIO" documentation regarding acceptable naming
# formats for Pins.

# General Program Constants.
PULSE_AVG_NUM  = 5		# Pulses to average before state transitions.
PULSE_WID_MAX  = 14		# Input signal maximum duty cycle [%].
PULSE_WID_MIN  = 7		# Input signal minimum duty cycle [%].
PULSE_WID_TOL  = 25		# Tolerance on Pulse Width Deviations [gap %].
PULSE_WID_FREQ = 70		# Expected signal frequency [Hz].

POS_HIST_NUM = 5		# Previous Position Commands to compare against
						#	before actuator motions.

# Linear Actuator Constants.
PIN_LIN_IN   = "P8_12"		# Pin for Input PWM from RC Controller.
PIN_LIN_ENA  = "P9_16"		# Pin for Output High Enable Signal.
PIN_LIN_OUT1 = "P9_14"		# Pin for Output High/Low to Driver CH1.
PIN_LIN_OUT2 = "P9_12"		# Pin for Output High/Low to Driver CH2.

LIN_STROKE_MAX    = 2		# Maximum stroke length [inch].
LIN_STROKE_TARGET = 1.5		# Target stroke length [inch].

# Carousel Stepper Constants.
# TODO(vjon@alumni.ubc.ca): Define Pins

# Shoulder Stepper Constants.
# TODO(vjon@alumni.ubc.ca): Define Pins

# Pressure Transducer Constants.
# TODO(vjon@alumni.ubc.ca): Define Pins

def main():
	"""Translates RC Controller Input to appropriate actuator signals.
	
	This function utilizes a set of initial variable values to setup desired 
	functionality parameters (e.g. actuator stroke length), then enters a 
	polling loop to continually check the state of the input signals. Upon 
	proper conditions being met, changes in these inputs cause the program to 
	enter and iterate through one of three state machines (one for each of the 
	actuators on the SRS).
	
	Args:
		N/A
	
	Returns:
		N/A
	"""
	# Initialize Pins.
	GPIO.setup(LIN_IN, GPIO.IN)
	GPIO.setup(LIN_ENA, GPIO.OUT)
	GPIO.setup(LIN_OUT1, GPIO.OUT)
	GPIO.setup(LIN_OUT2, GPIO.OUT)
	# TODO(vjon@alumni.ubc.ca): Continue with remaining Pins.
	
	# Initialize Variables.
	