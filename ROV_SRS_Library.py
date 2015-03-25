# Copyright [2015], [Jonathan Lee]
# Distributed under the terms of the BSD 3-Clause License
#
#
# ROV_SRS_Library
#
#
# Overview:	A collection of helper functions used by the BeagleBone
#		to control the ROV SRS Actuators.
#
# Authors:	Jonathan Lee (2015)
#

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM

def calc_pulse_width(pin_name):
	"""Calculates the pulse width of a PWM signal input.

	Stores the time of day on a Rising Edge and subsequent Falling Edge
	event, then returns the difference in milliseconds.

	Args:
		pin_name: A String containing the pin name on which the PWM
			signal is expected. The pin name should be in the
			format defined by the Adafruit_BBIO library.
	
	Returns:
		A float containing the calculated pulse width, in
			milliseconds.
	"""

