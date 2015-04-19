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

def calc_pulse_width(pin_name, avg_num, sig_freq):
	"""Calculate the pulse width of a PWM signal input.

	This function stores the time of day on a Rising Edge and subsequent 
	Falling Edge event, calculates the average of multiple such events, 
	and returns the difference in milliseconds. Function will halt if run 
	on 0 or 100% Duty Cycle signals.

	Args:
		pin_name:		A String specifying the pin name on which the PWM 
						signal is expected. The pin name should be in the 
						format defined by the Adafruit_BBIO library.
		avg_num:		An Integer specifying the sample size.
		sig_freq:		An Integer specifying the expected frequency of 
						the PWM signal [Hz].
	
	Returns:
		pulse_avg:		The calculated pulse width [milliseconds].
	"""
	pulse_avg = 0.0
	__rise_flag = 0.0
	__fall_flag = 0.0
	__pulse_width = 0.0
	
	for i in range(avg_num)
		# Determine incoming signal Pulse Width.
		GPIO.wait_for_edge(pin_name, GPIO.RISING)
		__rise_flag = time.time()
		GPIO.wait_for_edge(pin_name, GPIO.FALLING)
		__fall_flag = time.time()
		__pulse_width = __fall_flag - __rise_flag
		
		# Adjust for missed Pulses (CPU busy during Edge event).
		# This is done by subtracting the PWM period value if the
		# measured pulse width is found to be greater than the period.
		while __pulse_width > (1/signal_freq)
			__pulse_width -= (1/signal_freq)
		
		pulse_avg += __pulse_width
	
	return (pulse_avg /= avg_num)

def set_position(pwm_width, sig_freq, sig_max, sig_min, sig_tol):
	"""Set the position command corresponding to a PWM pulse width.
	
	This function checks if the pulse width value provided falls within
	the tolerance range of the expected maximum or minimum pulse width
	values and returns the corresponding position command.
	
	Args:
		pwm_width:		A float specifying the measured pulse width
						[milliseconds].
		sig_freq:		An integer specifying the expected frequency
						of the PWM signal [Hz].
		sig_max:		An integer specifying the maximum expected
						duty cycle of the PWM signal [%].
		sig_min:		An integer specifying the minimum expected
						duty cycle of the PWM signal [%].
		sig_tol:		An integer specifying the acceptable tolerance
						on deviations in the measured pulse width from
						the expected values. The excepted values
						correspond to the pulse widths of the maximum
						and minimum expected duty cycle values specified
						above. The tolerance is expressed relative to
						the millisecond difference between the maximum 
						and minimum possible pulse widths [%].
	
	Returns:
		pos_cmd:		The position command corresponding to the
						measured pulse width.
						2  == maximum pulse width.
						1  == intermediate pulse width.
						0  == minimum pulse width.
						-1 == error value
	"""
	pos_cmd = 0
	__pwm_width_max = ((1/signal_freq)*(sig_max/100))
	__pwm_width_min = ((1/signal_freq)*(sig_min/100))
	__pwm_width_tol = (__pwm_width_max - __pwm_width_min)*(sig_tol/100)
	
	# Check absolute maximum allowable value.
	if pwm_width < (__pwm_width_max + __pwm_width_tol)
		# Check against multiple minimum values.
		if pwm_width >= (__pwm_width_max - __pwm_width_tol)
			pos_cmd = 2
		elif pwm_width >= (__pwm_width_min + __pwm_width_tol)
			pos_cmd = 1
		elif pwm_width >= (__pwm_width_min - __pwm_width_tol)
			pos_cmd = 0
		else
			pos_cmd = -1
	else
		pos_cmd = -1
	
	return pos_cmd

def move_linear(la_hist, hist_len, la_out1, la_out2, stroke):
	"""Move the linear actuator to match the desired position command.
	
	This function checks for a transition within a series of position
	commands and changes the position of the linear actuator when the
	most recent command has persisted for half the length of the position 
	command history series.
	
	Args:
		la_hist:		A deque containing the history of position
						commands, which are themselves integers with
						values between -1 and 2. Refer to set_position()
						Returns: "pos_cmd" for further details.
		hist_len:		An integer specifying the length of the "la_hist"
						deque.
		la_out1:		A string specifying the pin name on which the first
						output signal should be sent.
		la_out2:		A string specifying	the pin name on which the second
						output signal should be sent.
		stroke:			A float specifying the stroke fraction desired for
						the shaft movement.
	
	Returns:
		N/A
	"""
	max_stroke_time = 2		# Experimentally determined for the Firgelli
							#	L16-P Linear Actuator
	
	end_flag = True
	end_index = hist_len
	
	# Check for duration of newest Command.
	while end_flag is True and end_index >= 0
		if la_hist[end_index] is la_hist[hist_len]
			end_index -= 1
		else
			end_flag = False
	
	start_flag = True
	start_count = 0
	
	# Check for duration of oldest Command.
	while start_flag is True and start_index < hist_len
		if la_hist[start_index] is la_hist[0]
			start_index += 1
		else
			start_flag = False
			
	# Change Linear Actuator Position if Command History meets criteria.
	if start_flag is True and end_flag is True
		if la_hist[hist_len] is 2
			# Retract Linear Actuator for specific amount of time.
			GPIO.output(PIN_LA_OUT1, GPIO.LOW)
			GPIO.output(PIN_LA_OUT2, GPIO.HIGH)
			time.sleep(max_stroke_time*stroke)
		elif la_hist[hist_len] is 0
			# Extend Linear Actuator for full amount of time.
			GPIO.output(PIN_LA_OUT1, GPIO.HIGH)
			GPIO.output(PIN_LA_OUT2, GPIO.LOW)
			time.sleep(max_stroke_time)
	
	# Hold Linear Actuator at desired Position.
	GPIO.output(PIN_LA_OUT1, GPIO.LOW)
	GPIO.output(PIN_LA_OUT2, GPIO.LOW)
	
