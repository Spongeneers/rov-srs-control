# Copyright 2015, Jonathan Lee
# Distributed under the terms of the BSD 3-Clause License
#
#
# ROV_SRS_Library
#
#
# Overview:	A collection of helper functions used by the BeagleBone
#		to control the ROV SRS Actuators.
#
# Authors:	Jonathan Lee
#

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import time

def calc_pulse_width(pin_name, signal_freq):
	"""Calculates the pulse width of a PWM signal input.

	Stores the time of day on a Rising Edge and subsequent Falling Edge event, 
	then returns the difference in milliseconds. Function will halt if run
	against 0% or 100% Duty Cycle signals.

	Args:
		pin_name: 			A String specifying the pin name on which the PWM 
							signal is expected. The pin name should be in the 
							format defined by the Adafruit_BBIO library.
		signal_freq:		An Integer specifying the expected frequency of the 
							PWM signal [Hz].
	
	Returns:
		__pulse_width:		The calculated pulse width [milliseconds].
	"""	
	# Determine incoming signal Pulse Width.
	GPIO.wait_for_edge(pin_name, GPIO.RISING)
	__rise_flag = time.time()
	GPIO.wait_for_edge(pin_name, GPIO.FALLING)
	__fall_flag = time.time()
	__pulse_width = __fall_flag - __rise_flag
	
	# Adjust for missed Pulses (CPU busy during Edge event).
	while __pulse_width > (1/signal_freq)
		__pulse_width -= (1/signal_freq)
		
	return __pulse_width

def check_pulse_width():