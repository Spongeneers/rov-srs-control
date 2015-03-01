# Copyright 2015, Jonathan Lee
# Distributed under the terms of the BSD 3-Clause License
#
#
# ROV_SRS_Library
#
#
# Overview:	A collection of helper functions used by the BeagleBone Black
#		to control the ROV SRS Actuators.
#
# Authors:	Jonathan Lee
#

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import time

#
# Constant Definitions.
#

# Hardware-related Constants.
LA_STROKE_TIME = 2		# Firgelli L16-P: Full stroke time [sec].
CS_STEP_ANGLE = 1.8		# Soyo Unipolar: Step Angle [degrees].
SS_STEP_ANGLE = 1.8		# Soyo Unipolar: Step Angle [degrees].

def calc_width(pin, size, freq):
	"""Calculate the Pulse Width of a PWM input signal.

	This function stores the time of day on a Rising Edge and subsequent 
	Falling Edge event, calculates the average of multiple such events, 
	and returns the difference in milliseconds. Function will halt if run 
	on 0 or 100% Duty Cycle signals.

	Args:
		pin:		A String specifying the pin name on which the PWM 
					signal is expected. The pin name should be in the 
					format defined by the Adafruit_BBIO library.
		size:		An Integer specifying the sample size.
		freq:		An Integer specifying the expected frequency of 
					the PWM signal [Hz].
	
	Returns:
		avg:		The calculated Pulse Width [milliseconds].
	"""
	avg = 0.0
	__rise_flag = 0.0
	__fall_flag = 0.0
	__pulse_width = 0.0
	
	for i in range(size)
		# Determine incoming signal Pulse Width.
		GPIO.wait_for_edge(pin, GPIO.RISING)
		__rise_flag = time.time()
		GPIO.wait_for_edge(pin, GPIO.FALLING)
		__fall_flag = time.time()
		__pulse_width = __fall_flag - __rise_flag
		
		# Adjust for missed Pulses (CPU busy during Edge event).
		# This is done by subtracting the PWM period value if the
		# measured pulse width is found to be greater than the period.
		while __pulse_width > (1/freq)
			__pulse_width -= (1/freq)
		
		avg += __pulse_width
	
	return (avg /= size)

def set_position(width, freq, max, min, tol):
	"""Set the Position Command corresponding to a PWM Pulse Width.
	
	This function checks if the Pulse Width value provided falls within
	the tolerance range of the expected maximum or minimum Pulse Width
	values and returns the corresponding Position Command.
	
	Args:
		width:		A float specifying the measured Pulse Width
					[milliseconds].
		freq:		An integer specifying the expected frequency
					of the PWM signal [Hz].
		max:		An integer specifying the maximum expected
					duty cycle of the PWM signal [%].
		min:		An integer specifying the minimum expected
					duty cycle of the PWM signal [%].
		tol:		An integer specifying the acceptable tolerance
					on deviations in the measured Pulse Width from
					the expected values. The excepted values
					correspond to the Pulse Widths of the maximum
					and minimum expected duty cycle values specified
					above. The tolerance is expressed relative to
					the millisecond difference between the maximum 
					and minimum possible Pulse Widths [%].
	
	Returns:
		cmd:		The Position Command corresponding to the
					measured Pulse Width.
					2  == Maximum Pulse Width.
					1  == Intermediate Pulse Width .
					0  == Minimum Pulse Width.
					-1 == Error.
	"""
	cmd = -1
	__pwm_width_max = ((1/freq)*(max/100))
	__pwm_width_min = ((1/freq)*(min/100))
	__pwm_width_tol = (__pwm_width_max - __pwm_width_min)*(tol/100)
	
	# Check absolute maximum allowable value.
	if width < (__pwm_width_max + __pwm_width_tol)
		# Check against multiple minimum values.
		if width >= (__pwm_width_max - __pwm_width_tol)
			cmd = 2
		elif width >= (__pwm_width_min + __pwm_width_tol)
			cmd = 1
		elif width >= (__pwm_width_min - __pwm_width_tol)
			cmd = 0
	
	return cmd

def check_trend(hist, length):
	"""Check for Position Command persistance.
	
	This function returns the most recent in a series of Position
	Commands if the series exhibits a 50/50 split between two different
	types of Position Commands.
	
	Args:
		hist:		A deque containing the history of Position
					Commands, which are themselves integers with
					values between -1 and 2. Refer to function Returns
					for further details.
		length:		An integer specifying the length of the "hist" deque.
	
	Returns:
		trend:		The persistant value of the Command series 2nd half.
					2  == Maximum Pulse Width.
					1  == Intermediate Pulse Width.
					0  == Minimum Pulse Width.
					-1 == Error.
	"""
	trend = -1
	__start_flag = True
	__end_flag = True
	__start_index = 0
	__end_index = length
	
	# Check for duration of oldest Command.
	while __start_flag is True and __start_index < length
		if hist[__start_index] is hist[0]
			__start_index += 1
		else
			__start_flag = False
	
	# Check for duration of newest Command.
	while __end_flag is True and __end_index >= 0
		if hist[__end_index] is hist[length]
			__end_index -= 1
		else
			__end_flag = False
			
	# Check for 50/50 command split.
	if start_flag is True and end_flag is True
		trend = hist[length]
	
	return trend
	
def move_linear(cmd, out1, out2, stroke):
	"""Move the Linear Actuator to match the desired Position Command.
	
	This function changes the Position of the Linear Actuator in
	accordance with the input Position Command.
	
	Args:
		cmd:		The Position Command to enact.
					2  == Retract Linear Actuator (Open Gripper).
					1  == Lock current Position.
					0  == Extend Linear Actuator (Close Gripper).
					-1 == Error
		out1:		A string specifying the pin name on which the Extend
					output signal should be sent.
		out2:		A string specifying	the pin name on which the Retract
					output signal should be sent.
		stroke:		A float specifying the stroke fraction desired for
					the shaft movement.
	
	Returns:
		N/A
	"""
	if cmd is 2
		# Retract Linear Actuator for specific amount of time.
		GPIO.output(out1, GPIO.LOW)
		GPIO.output(out2, GPIO.HIGH)
		time.sleep(LA_STROKE_TIME*stroke)
	elif cmd is 0
		# Extend Linear Actuator for full amount of time.
		GPIO.output(out1, GPIO.HIGH)
		GPIO.output(out2, GPIO.LOW)
		time.sleep(LA_STROKE_TIME)
	# TODO: Error handling.

	# Hold Linear Actuator at desired Position.
	GPIO.output(out1, GPIO.LOW)
	GPIO.output(out2, GPIO.LOW)
	
def move_carousel(cmd, out1, out2, out3, out4, angle):
	"""Move the Carousel Stepper to match the desired Position Command.
	
	This function changes the Position of the Carousel Stepper in
	accordance with the input Position Command.
	
	Args:
		cmd:		The Position Command to enact.
					2  == Advance Carousel Stepper (Change Gripper).
					1  == Lock current Position.
					0  == Lock current Position.
					-1 == Error.
		out1:		A string specifying the pin name on which the Phase A
					Switch 1 signal should be sent.
		out2:		A string specifying	the pin name on which the Phase A
					Switch 2 signal should be sent.
		out3:		A string specifying the pin name on which the Phase B
					Switch 1 signal should be sent.
		out4:		A string specifying	the pin name on which the Phase B
					Switch 2 signal should be sent.
		angle:		A float specifying the circle fraction desired for
					the shaft rotation.
	
	Returns:
		N/A
	"""

def move_shoulder(cmd, out1, out2, out3, out4, step):
	"""Move the Shoulder Stepper to match the desired Position Command.
	
	This function changes the Position of the Shoulder Stepper in
	accordance with the input Position Command.
	
	Args:
		cmd:		The Position Command to enact.
					2  == Step Clockwise (Tilt Down).
					1  == Lock current Position.
					0  == Step Counter-Clockwise (Tilt Up).
					-1 == Error.
		out1:		A string specifying the pin name on which the Phase A
					Switch 1 signal should be sent.
		out2:		A string specifying	the pin name on which the Phase A
					Switch 2 signal should be sent.
		out3:		A string specifying the pin name on which the Phase B
					Switch 1 signal should be sent.
		out4:		A string specifying	the pin name on which the Phase B
					Switch 2 signal should be sent.
		step:		An integer specifying the next Phase sequence for
					continued rotation.
	
	Returns:
		N/A
	"""