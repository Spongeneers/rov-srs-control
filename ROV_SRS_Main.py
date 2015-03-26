#!/usr/bin/python
# Copyright [2015], [Jonathan Lee]
# Distributed under the terms of the BSD 3-Clause License
#
#
# ROV_SRS_Main
#
#
# Overview:	The main runtime script to handle SRS Control.
#
# Authors:	Jonathan Lee (2015)
#

import ROV_SRS_Library as ROV
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM

# Define Module-level Constants.
#
# Refer to the "Adafruit_BBIO" documentation regarding acceptable naming
# formats for Pins.

# General Program Constants.
PULSE_NUM_AVG = 5			# Number of Pulses to average before state transitions.
PULSE_WID_HI = 0.002		# Input Pulse Width (70 Hz, 14% Duty Cycle) [msec].
PULSE_WID_LO = 0.001		# Input Pulse Width (70 Hz, 7% Duty Cycle) [msec].
PULSE_WID_TOL = 0.00025		# Tolerance on Pulse Width Deviations [msec].
PULSE_WID_LIM = 0.014		# Upper Limit on Pulse Widths (70 Hz, 1 Period) [msec].

# Linear Actuator related Constants.
LIN_IN1 = "P8_12"		# Pin for Input PWM from RC Controller.
LIN_ENA = "P9_16"		# Pin for Output High Enable Signal.
LIN_OUT1 = "P9_14"		# Pin for Output High/Low to Driver CH1.
LIN_OUT2 = "P9_12"		# Pin for Output High/Low to Driver CH2.

def main():
	"""Translates RC Controller Input to appropriate actuator signals.
	
	This function utilizes a set of initial variable values to setup
	desired functionality parameters (e.g. actuator stroke length), then
	enters a polling loop to continually check the state of the input
	signals. Upon proper conditions being met, changes in these inputs
	cause the program to enter and iterate through one of three state
	machines (one for each of the actuators on board the SRS).
	
	Args:
		N/A
	
	Returns:
		N/A
	"""
	
	# Define Constant parameters.