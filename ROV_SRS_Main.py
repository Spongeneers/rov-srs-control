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

from collections import deque

from Adafruit_BBIO import ADC
from Adafruit_BBIO import GPIO
import ROV_SRS_Library as SRS

#
# Constant Definitions.
#

# General Program Constants.
PWM_AVG_NUM  = 5		# Pulses to average before saving Commands.
PWM_WID_FREQ = 70.0		# Expected signal frequency [Hz].
PWM_WID_MAX  = 14.0		# Input signal maximum duty cycle [%].
PWM_WID_MIN  = 7.0		# Input signal minimum duty cycle [%].
PWM_WID_TOL  = 20.0		# Tolerance on Pulse Width Deviations [%].

POS_HIST_NUM = 5		# Number of Position Commands to store.

# Linear Actuator Constants.
PIN_LA_IN  =  "P8_8"		# Pin for Input PWM from RC Controller.
PIN_LA_ENA =  "P8_13"		# Pin for Output-High Enable Signal.
PIN_LA_OUT = ["P8_11",		# Pin for Output to Driver CH1.
			  "P8_9"]		# Pin for Output to Driver CH2.

LA_STROKE_MAX    = 2		# Maximum stroke length [inch].
LA_STROKE_TARGET = 1.25		# Target stroke length [inch].

# Carousel Stepper Constants.
PIN_CS_IN  =  "P8_10"		# Pin for Input PWM from RC Controller.
PIN_CS_VCC =  "P8_27"		# Pin for Supply Voltage.
PIN_CS_OUT = ["P8_25",		# Pin for Output to Phase A Switch 1.
			  "P8_23",		# Pin for Output to Phase A Switch 2.
			  "P8_21",		# Pin for Output to Phase B Switch 1.
			  "P8_19"]		# Pin for Output to Phase B Switch 2.

CS_GRIPPER_NUM = 20			# Number of Grippers on ROV.

# Shoulder Stepper Constants.
PIN_SS_IN  =  "P8_26"		# Pin for Input PWM from RC Controller.
PIN_SS_VCC =  "P8_37"		# Pin for Supply Voltage.
PIN_SS_OUT = ["P8_35",		# Pin for Output to Phase A Switch 1.
			  "P8_33",		# Pin for Output to Phase A Switch 2.
			  "P8_31",		# Pin for Output to Phase B Switch 1.
			  "P8_29"]		# Pin for Output to Phase B Switch 2.

# Pressure Transducer Constants.
PIN_PT_IN  = "P9_39"		# Pin for Input Data from Transducer.
# TODO: Define Pins

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
	
	# Linear Actuator.
	GPIO.setup(PIN_LA_IN, GPIO.IN)
	GPIO.setup(PIN_LA_ENA, GPIO.OUT)
	for __col in range(len(PIN_LA_OUT)):
		GPIO.setup(PIN_LA_OUT[__col], GPIO.OUT)
	GPIO.output(PIN_LA_ENA, GPIO.HIGH)
	
	# Carousel Stepper.
	GPIO.setup(PIN_CS_IN, GPIO.IN)
	GPIO.setup(PIN_CS_VCC, GPIO.OUT)
	for __col in range(len(PIN_CS_OUT)):
		GPIO.setup(PIN_CS_OUT[__col], GPIO.OUT)
	
	# Shoulder Stepper.
	GPIO.setup(PIN_SS_IN, GPIO.IN)
	GPIO.setup(PIN_SS_VCC, GPIO.OUT)
	for __col in range(len(PIN_SS_OUT)):
		GPIO.setup(PIN_SS_OUT[__col], GPIO.OUT)
	
	# Pressure Transducer.
	ADC.setup()
	# TODO(Giles): Continue Pressure Transducer Initialization.
	
	#
	# Initialize Variables.
	#
	
	# Pulse Width Averages.
	la_avg = 0.0
	cs_avg = 0.0
	ss_avg = 0.0
	
	# Position Commands.
	la_cmd_hist = deque(
		(1 for i in range(POS_HIST_NUM)), maxlen = POS_HIST_NUM)
	la_trend = 0
	
	cs_cmd_hist = deque(
		(1 for i in range(POS_HIST_NUM)), maxlen = POS_HIST_NUM)
	cs_trend = 0
	
	ss_cmd_hist = deque(
		(1 for i in range(POS_HIST_NUM)), maxlen = POS_HIST_NUM)
	ss_trend = 0
	
	# Shoulder Stepper: Step sequence counter.
	ss_step = 0
	
	#
	# Main program polling loop.
	#
	while True:
		#
		# Linear Actuator polling.
		#
		
		# Determine Average Pulse Width.
		la_avg = SRS.calc_width(
			PIN_LA_IN, PWM_AVG_NUM, PWM_WID_FREQ)

		# Add new Position Command to History.
		la_cmd_hist.append(SRS.set_position(
			la_avg,
			PWM_WID_FREQ, PWM_WID_MAX, PWM_WID_MIN, PWM_WID_TOL))
	
		# Check for Position Command Persistance.
		la_trend = SRS.check_trend(la_cmd_hist)

		# Process Position Command.
		SRS.move_linear(
			la_trend,
			PIN_LA_OUT, (LA_STROKE_TARGET/LA_STROKE_MAX))
		
		#
		# Carousel Stepper polling.
		#
		
		# Determine Average Pulse Width.
	#	cs_avg = SRS.calc_width(
	#		PIN_CS_IN, PWM_AVG_NUM, PWM_WID_FREQ)

		# Add new Position Command to History.
	#	cs_cmd_hist.append(SRS.set_position(
	#		cs_avg,
	#		PWM_WID_FREQ, PWM_WID_MAX, PWM_WID_MIN, PWM_WID_TOL))

		# Check for Position Command Persistance.
	#	cs_trend = SRS.check_trend(cs_cmd_hist)

		# Process Position Command.
	#	SRS.move_carousel(
	#		cs_trend,
	#		PIN_CS_OUT, (1/CS_GRIPPER_NUM))
		
		#
		# Shoulder Stepper polling.
		#
		
		# Determine Average Pulse Width.
	#	ss_avg = SRS.calc_width(
	#		PIN_SS_IN, PWM_AVG_NUM, PWM_WID_FREQ)
		
		# Add new Position Command to History.
	#	ss_cmd_hist.append(SRS.set_position(
	#		ss_avg,
	#		PWM_WID_FREQ, PWM_WID_MAX, PWM_WID_MIN, PWM_WID_TOL))

		# Check for Position Command Persistance.
	#	ss_trend = SRS.check_trend(ss_cmd_hist)

		# Process Position Command.
	#	ss_step = SRS.move_shoulder(
	#		ss_trend,
	#		PIN_SS_OUT,
	#		ss_step)

		#
		# Pressure Transducer polling.
		#
		
		# TODO
