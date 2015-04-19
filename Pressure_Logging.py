# Copyright 2015, Giles Fernandes
# Distributed under the terms of the BSD 3-Clause License
#
#
# ROV_SRS_Library
#
#
# Overview:		
#
#
# Authors:		Giles Fernandes
#

# 1.8V is the MAXIMUM voltage on the AIN pins

"AIN0", "P9_39"

import Adafruit_BBIO.ADC as ADC
import sys
import datetime
from datetime import datetime

ADC.setup()

def logfile_setup(fname):
    """Creates File with the date appended to the name
	
    Args:
			fname:				File Name
	
    Returns:
			N/A	
    """

	__fmt = '%Y-%m-%d_{fname}'
	
	# Create name with timestamp appended
	datename =  datetime.datetime.now().strftime(__fmt).format(fname = fname)
	
	# Open the file in write mode
	file = open( datename,'w')


def log_pressure(pin_name):
	"""Logs the pressure difference into a csv file
	
	Reads the pressure using the read_pressure function and writes a time stamp
	and pressure value to the file.
			
	TODO: Check to make sure memory is available for writing.
			Add file opening and closing in the main.
	
	Args:
			pin_name:				A String specifying the pin name on which the PWM 
											signal is expected. The pin name should be in the 
											format defined by the Adafruit_BBIO library.
			read_freq:				An Integer specifying the desired reading frequency
									of the pressure sensor [Hz]
	
	Returns:
			N/A	
	"""
		
	
	__diff = read_pressure()

	# TODO Check if memory has been filled
		
	# If memory has not been filled, write to file
	
	# Format: Time  Pressure difference
	file.write(datetime.now().strftime('%H:%M:%S'))
	file.write("\t")
	file.write(str(__diff))
	file.write("\n")
	
	
		
def read_pressure(pin_name):
	"""Reads the pressure sensor analog input and converts to a pressure differential 
	
	Args:
			pin_name:		BeagleBone Analog Pin to read from
	
	Returns:
			__diff:			The calculated pressure difference [psi]
	"""
	
	#Analog read voltage of the pressure differential sensor
	__diff = ADC.read_raw(pin_name)	
	
	#TODO: Map voltage value to pressure differential	
	
	return __diff
	