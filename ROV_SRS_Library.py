# Copyright 2015, Giles Fernandes, Jonathan Lee
# Distributed under the terms of the BSD 3-Clause License
#
#
# ROV_SRS_Library
#
#
# Overview:	A collection of helper functions used by the BeagleBone Black
#		to control the ROV SRS Actuators.
#
# Authors:	Giles Fernandes, Jonathan Lee
#

from datetime import datetime
from collections import deque
import sys
import time

import Adafruit_BBIO.ADC as ADC
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM

#
# Constant Definitions.
#

# Hardware-related Constants.
LA_STROKE_TIME = 1.6	# Firgelli L16-P: Full stroke time [sec].
CS_STEP_ANGLE = 1.8		# Soyo Unipolar: Step Angle [degrees].
SS_STEP_ANGLE = 1.8		# Soyo Unipolar: Step Angle [degrees].

# Command Library for Linear Actuator.
LA_COMMANDS = [[GPIO.HIGH, GPIO.LOW],		# Extend Actuator.
			   [GPIO.LOW, GPIO.LOW],		# Hold Actuator.
			   [GPIO.LOW, GPIO.HIGH]]		# Retract Actuator.

# Half-stepping command sequence for Two-Phase Unipolar Steppers.
STEP_SEQUENCE = [[GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.LOW],
				 [GPIO.HIGH, GPIO.LOW, GPIO.HIGH, GPIO.LOW],
				 [GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.LOW],
				 [GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW],
				 [GPIO.LOW, GPIO.HIGH, GPIO.LOW, GPIO.LOW],
				 [GPIO.LOW, GPIO.HIGH, GPIO.LOW, GPIO.HIGH],
				 [GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.HIGH],
				 [GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH]]

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
		width:		A Float specifying the measured Pulse Width
					[milliseconds].
		freq:		An Integer specifying the expected frequency
					of the PWM signal [Hz].
		max:		An Integer specifying the maximum expected
					duty cycle of the PWM signal [%].
		min:		An Integer specifying the minimum expected
					duty cycle of the PWM signal [%].
		tol:		An Integer specifying the acceptable tolerance
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
		hist:		A Deque containing the history of Position
					Commands, which are themselves integers with
					values between -1 and 2. Refer to function Returns
					for further details.
		length:		An Integer specifying the length of the "hist" deque.
	
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
	
def move_linear(cmd, out, stroke):
	"""Move the Linear Actuator to match the desired Position Command.
	
	This function changes the Position of the Linear Actuator in
	accordance with the input Position Command.
	
	Args:
		cmd:		The Position Command to enact.
					2  == Retract Linear Actuator (Open Gripper).
					1  == Lock current Position.
					0  == Extend Linear Actuator (Close Gripper).
					-1 == Error
		out:		An Array of Strings specifying the pin names on which 
					the output signals should be sent.
		stroke:		A Float specifying the stroke fraction desired for
					the shaft movement.
	
	Returns:
		N/A
	"""
	if cmd is 2 or cmd is 0
		# Begin Linear Actuator motion.
		for __col in range(len(out))
			GPIO.output(out(__col), LA_COMMANDS[__col][cmd])

		if cmd is 2
			# Retract Linear Actuator for specific amount of time.
			time.sleep(LA_STROKE_TIME*stroke)
		elif cmd is 0
			# Extend Linear Actuator for full amount of time.
			time.sleep(LA_STROKE_TIME)

	elif cmd is -1
		# TODO(Jonathan): Error handling.
		pass

	# Hold Linear Actuator at desired Position.
	for __index in range(len(out))
		GPIO.output(out(__index), GPIO.LOW)
	
def move_carousel(cmd, out, angle):
	"""Move the Carousel Stepper to match the desired Position Command.
	
	This function changes the Position of the Carousel Stepper in
	accordance with the input Position Command.
	
	Args:
		cmd:		The Position Command to enact.
					2  == Advance Carousel Stepper (Change Gripper).
					1  == Lock current Position.
					0  == Lock current Position.
					-1 == Error.
		out:		An Array of Strings specifying the pin names on which 
					the output signals should be sent.
		angle:		A Float specifying the circle fraction desired for
					the shaft rotation.
	
	Returns:
		N/A
	"""
	if cmd is 2
		# Calculate required number of half-steps.
		__path_steps = (angle*360)/(CS_STEP_ANGLE/2)
	
		# Rotate Carousel Stepper to specific angle.
		for __row in range(__path_steps)
			# Determine next command in step sequence to issue.
			__step = __row
			while __step >= len(STEP_SEQUENCE)
				__step -= len(STEP_SEQUENCE)
			
			# Set pin voltages to correspond to sequence.
			for __col in range(len(out))
				GPIO.output(out[__col], STEP_SEQUENCE[__col][__step])
				
	elif cmd is -1
		# TODO(Jonathan): Error handling.
		pass
		
	else
		# Hold Carousel Stepper at desired Position.
		for __index in range(len(out))
			GPIO.output(out[__index], GPIO.LOW)

def move_shoulder(cmd, out, step):
	"""Move the Shoulder Stepper to match the desired Position Command.
	
	This function changes the Position of the Shoulder Stepper in
	accordance with the input Position Command.
	
	Args:
		cmd:		The Position Command to enact.
					2  == Step Clockwise (Tilt Down).
					1  == Lock current Position.
					0  == Step Counter-Clockwise (Tilt Up).
					-1 == Error.
		out:		An Array of Strings specifying the pin names on which 
					the output signals should be sent.
		step:		An Integer specifying the Phase sequence to be
					executed.
	
	Returns:
		next:		An Integer specifying the next Phase sequence for
					continued rotation.
	"""
	# Determine command in step sequence to issue.
	while step >= len(STEP_SEQUENCE)
		step -= len(STEP_SEQUENCE)
	while step < 0
		step += len(STEP_SEQUENCE)

	next = step
	
	if cmd is 2 or cmd is 0
		# Advance Shoulder Stepper one step.
		for __col in range(len(out))
			GPIO.output(out[__col], STEP_SEQUENCE[__col][step])
		
		# Set next step sequence based on direction of rotation.
		if cmd is 2
			next += 1
		elif cmd is 0
			next -= 1
		
	elif cmd is -1
		# TODO(Jonathan): Error handling.
		pass
	
	else
		# Hold Shoulder Stepper at desired Position.
		for __index in range(len(out))
			GPIO.output(out[__index], GPIO.LOW)
	
	return next
	
def setup_logfile(name):
    """Create File for data logging.
	
	This function creates a CSV file, appends the current date to the
	filename, and opens the file for data recording.
	
    Args:
		name:		A String specifying the desired file name. The current
					date will be appended to this string.
	
    Returns:
		N/A	
    """
	__fmt = '%Y-%m-%d_{name}'
	
	# Create name with timestamp appended.
	datename = datetime.datetime.now().strftime(__fmt).format(name = name)
	
	# Open the file in write mode.
	file = open(datename,'w')

def read_pressure(pin):
	"""Read the pressure sensor value.

	This function reads the analog input from the pressure sensor and 
	returns the corresponding pressure differential value.
	
	Args:
		pin:		A String specifying the pin name on which the 
					pressure sensor signal is expected.
	
	Returns:
		__diff:		The calculated pressure difference [psi].
	"""
	# Analog read voltage of the pressure differential sensor.
	__diff = ADC.read_raw(pin)	
	
	# TODO(Giles): Map voltage value to pressure differential.	
	
	return __diff
	
def log_pressure(pin, freq):
	"""Log the pressure difference into the log file.
	
	This function reads the pressure from the sensor and writes a time 
	stamp and pressure value to a CSV log file.
	
	Args:
		pin:		A String specifying the pin name on which the 
					pressure sensor signal is excepted.
		freq:		An Integer specifying the desired logging 
					frequency [Hz].
	
	Returns:
		N/A	
	"""
	__diff = read_pressure(pin)

	# TODO(Giles): Check if memory has been filled.
	# If memory has not been filled, write to file.
	
	# Log Format: Time,Pressure
	file.write(datetime.now().strftime('%H:%M:%S'))
	file.write("\t")
	file.write(str(__diff))
	file.write("\n")