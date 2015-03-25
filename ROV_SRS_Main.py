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

