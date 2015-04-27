# Copyright 2015, Giles Fernandes, Jonathan Lee
# Distributed under the terms of the BSD 3-Clause License
#
#
# ROV_SRS_Library
#
#
# Overview: A collection of helper functions used by the BeagleBone Black
#     to control the ROV SRS Actuators.
#
# Authors:  Giles Fernandes, Jonathan Lee
#

from collections import deque
from datetime import datetime
import sys
import time

from Adafruit_BBIO import ADC
from Adafruit_BBIO import GPIO

#
# Constant Definitions.
#

# Hardware-related Constants.
LA_MAX_STROKE = 2.0              # Firgelli L16-P: Max Stroke length [inch].
CS_STEP_ANGLE = 1.8              # Soyo Unipolar: Step Angle [degrees].
SS_STEP_ANGLE = 1.8              # Soyo Unipolar: Step Angle [degrees].
CS_DRIVE_STEP_PERSIST = 0.01     # Big Easy Driver: Min Persist Time [sec].
SS_DRIVE_STEP_PERSIST = 0.01     # Easy Driver: Min Persist Time [sec].

# Command Library for Linear Actuator.
LA_COMMANDS = [[GPIO.HIGH, GPIO.LOW],     # Extend Actuator.
               [GPIO.LOW, GPIO.LOW],      # Hold Actuator.
               [GPIO.LOW, GPIO.HIGH]]     # Retract Actuator.

# Command Library for Carousel Stepper.
CS_COMMANDS = [[GPIO.LOW, GPIO.LOW],      # Hold Stepper in place.
               [GPIO.LOW, GPIO.LOW],      # Hold Stepper in place.
               [GPIO.LOW, GPIO.HIGH]]     # Take one Step CW.

# Command Library for Shoulder Stepper.
SS_COMMANDS = [[GPIO.HIGH, GPIO.HIGH],    # Take one Step CCW.
               [GPIO.LOW, GPIO.LOW],      # Hold Stepper in place.
               [GPIO.LOW, GPIO.HIGH]]     # Take one Step CW.

def get_width(pin, size, freq, max, min, tol):
    """Calculate the Pulse Width of a PWM input signal.

    This function stores the time of day on a Rising Edge and subsequent 
    Falling Edge event, calculates the average of multiple such events, 
    and returns the difference in milliseconds. Function will halt if run 
    on 0 or 100% Duty Cycle signals.

    Args:
        pin:        A String specifying the pin name on which the PWM 
                    signal is expected. The pin name should be in the 
                    format defined by the Adafruit_BBIO library.
        size:       An Integer specifying the sample size.
        freq:       A float specifying the expected frequency of 
                    the PWM signal [Hz].
        max:        A Float specifying the maximum expected
                    duty cycle of the PWM signal [%].
        min:        A Float specifying the minimum expected
                    duty cycle of the PWM signal [%].
        tol:        A Float specifying the acceptable tolerance
                    on deviations in the measured Pulse Width from
                    the expected values. The excepted values
                    correspond to the Pulse Widths of the maximum
                    and minimum expected duty cycle values specified
                    above. The tolerance is expressed relative to
                    the millisecond difference between the maximum 
                    and minimum possible Pulse Widths [%].

    Returns:
        avg:        The calculated Pulse Width [milliseconds].
    """
    __WIDTH_MAX = ((1/freq)*(max/100))
    __WIDTH_MIN = ((1/freq)*(min/100))
    __WIDTH_TOL = (__WIDTH_MAX - __WIDTH_MIN)*(tol/100)

    avg = 0.0

    __rise_flag = 0.0
    __fall_flag = 0.0
    __pwm_width = 0.0

    for i in range(size):
        # Determine incoming signal Pulse Width.
        GPIO.wait_for_edge(pin, GPIO.RISING)
        __rise_flag = time.time()

        GPIO.wait_for_edge(pin, GPIO.FALLING)
        __fall_flag = time.time()

        __pwm_width = __fall_flag - __rise_flag

        # Correct for faulty values (missed edge events, etc.)
        while __pwm_width >= (1/freq):
            __pwm_width -= (1/freq)
        while __pwm_width > (__WIDTH_MAX + __WIDTH_TOL):
            __pwm_width -= __WIDTH_TOL
        while __pwm_width < (__WIDTH_MIN - __WIDTH_TOL):
            __pwm_width += __WIDTH_TOL

        avg += __pwm_width

    avg /= size

    return avg

def set_position(width, freq, max, min, tol):
    """Set the Position Command corresponding to a PWM Pulse Width.

    This function checks if the Pulse Width value provided falls within
    the tolerance range of the expected maximum or minimum Pulse Width
    values and returns the corresponding Position Command.

    Args:
        width:      A Float specifying the measured Pulse Width
                    [milliseconds].
        freq:       A Float specifying the expected frequency
                    of the PWM signal [Hz].
        max:        A Float specifying the maximum expected
                    duty cycle of the PWM signal [%].
        min:        A Float specifying the minimum expected
                    duty cycle of the PWM signal [%].
        tol:        A Float specifying the acceptable tolerance
                    on deviations in the measured Pulse Width from
                    the expected values. The excepted values
                    correspond to the Pulse Widths of the maximum
                    and minimum expected duty cycle values specified
                    above. The tolerance is expressed relative to
                    the millisecond difference between the maximum 
                    and minimum possible Pulse Widths [%].

    Returns:
        cmd:        The Position Command corresponding to the
                    measured Pulse Width.
                    2  == Maximum Pulse Width.
                    1  == Intermediate Pulse Width .
                    0  == Minimum Pulse Width.
    """
    __WIDTH_MAX = ((1/freq)*(max/100))
    __WIDTH_MIN = ((1/freq)*(min/100))
    __WIDTH_TOL = (__WIDTH_MAX - __WIDTH_MIN)*(tol/100)

    cmd = -1

    # Check pulse width bracket.
    if width >= (__WIDTH_MAX - __WIDTH_TOL):
        cmd = 2
    elif width >= (__WIDTH_MIN + __WIDTH_TOL):
        cmd = 1
    elif width >= (__WIDTH_MIN - __WIDTH_TOL):
        cmd = 0

    return cmd

def check_trend(hist, cont):
    """Check for Position Command persistance.

    This function returns the most recent in a series of Position
    Commands if the series exhibits the desired trend. Valid trends
    include a 50/50 split between two Command types or a continuous 
    sequence of one command type.

    Args:
        hist:       A Deque containing the history of Position
                    Commands, which are themselves integers with
                    values between -1 and 2. Refer to function Returns
                    for further details.
        cont:       A Boolean indicating whether a continuous command
                    sequence is expected.
                    True == Check for Continuous Command sequence.
                    False == Check for 50/50 Command sequence.

    Returns:
        trend:      The persistant value of the Command series 2nd half.
                    2  == Maximum Pulse Width.
                    1  == Intermediate Pulse Width.
                    0  == Minimum Pulse Width.
    """
    trend = -1

    __start_flag = True
    __end_flag = True
    __start_index = 0
    __end_index = (len(hist) - 1)

    # Check for duration of oldest Command.
    while __start_flag is True and __start_index < (len(hist) // 2):
        if hist[__start_index] is hist[0]:
            __start_index += 1
        else:
            __start_flag = False

    # Check for duration of newest Command.
    while __end_flag is True and __end_index >= (len(hist) // 2):
        if hist[__end_index] is hist[len(hist) - 1]:
            __end_index -= 1
        else:
            __end_flag = False

    # Check for desired Command trend.
    if cont is True and __end_flag is True:
        trend = hist[len(hist) - 1]
    elif __start_flag is True and __end_flag is True:
        if hist[0] is not hist[len(hist) - 1]:
            trend = hist[len(hist) - 1]

    return trend

def move_linear(cmd, out, pot, stroke):
    """Move the Linear Actuator to match the desired Position Command.

    This function changes the Position of the Linear Actuator in
    accordance with the input Position Command.

    Args:
        cmd:        The Position Command to enact.
                    2  == Retract Linear Actuator (Open Gripper).
                    1  == Lock current Position.
                    0  == Extend Linear Actuator (Close Gripper).
        out:        An Array of Strings specifying the pin names on which 
                    the output signals should be sent.
        pot:        A String specifying the pin name on which the input
                    Potentiometer signal is expected.
        stroke:     A Float specifying the stroke length desired for
                    the shaft movement.

    Returns:
        N/A
    """
    __UPPER_LIM = 1.0
    __LOWER_LIM = 1.0 - stroke/LA_MAX_STROKE

    __pot_pos = 0.0

    if cmd >= 0:
        # Begin Linear Actuator motion.
        for __col in range(len(out)):
            GPIO.output(out[__col], LA_COMMANDS[__col][cmd])

        # Check Potentiometer Signal.
        if cmd is 2:
            while __pot_pos > __LOWER_LIM:
                __pot_pos = ADC.read(pot)    # BUG: Adafruit_BBIO.ADC Library
                __pot_pos = ADC.read(pot)    # requires two read operations to
                                             # obtain updated values.
        elif cmd is 0:
            while __pot_pos < __UPPER_LIM:
                __pot_pos = ADC.read(pot)    # BUG: Adafruit_BBIO.ADC Library
                __pot_pos = ADC.read(pot)    # requires two read operations to
                                             # obtain updated values.

    # Hold Linear Actuator at desired Position.
    for __index in range(len(out)):
        GPIO.output(out[__index], GPIO.LOW)

def move_carousel(cmd, out, gripper):
    """Move the Carousel Stepper to match the desired Position Command.

    This function changes the Position of the Carousel Stepper in
    accordance with the input Position Command.

    Args:
        cmd:        The Position Command to enact.
                    2  == Advance Carousel Stepper (Change Gripper).
                    1  == Lock current Position.
                    0  == Lock current Position.
        out:        An Array of Strings specifying the pin names on which 
                    the output signals should be sent.
        gripper:    An Integer specifying the number of grippers currently
                    mounted on the Carousel.

    Returns:
        N/A
    """
    __path_steps = ((1/float(gripper))*360)/(CS_STEP_ANGLE)

    if cmd is 2:
        # Loop over single-step command.
        for __steps in range(int(__path_steps)):
            for __col in range((len(out))):
                GPIO.output(out[__col], CS_COMMANDS[cmd][__col])
            time.sleep(CS_DRIVE_STEP_PERSIST)

            GPIO.output(out[1], GPIO.LOW)
            time.sleep(CS_DRIVE_STEP_PERSIST)

    else:
        # Hold Carousel Stepper at desired Position.
        for __index in range(len(out)):
            GPIO.output(out[__index], GPIO.LOW)

def move_shoulder(cmd, out):
    """Move the Shoulder Stepper to match the desired Position Command.

    This function changes the Position of the Shoulder Stepper in
    accordance with the input Position Command.

    Args:
        cmd:        The Position Command to enact.
                    2  == Step Clockwise (Tilt Down).
                    1  == Lock current Position.
                    0  == Step Counter-Clockwise (Tilt Up).
        out:        An Array of Strings specifying the pin names on which 
                    the output signals should be sent.

    Returns:
        next:       An Integer specifying the next Phase sequence for
                    continued rotation.
    """
    if cmd is 2 or cmd is 0:
        for __col in range((len(out))):
            GPIO.output(out[__col], SS_COMMANDS[cmd][__col])
        time.sleep(SS_DRIVE_STEP_PERSIST)

        GPIO.output(out[1], GPIO.LOW)
        time.sleep(SS_DRIVE_STEP_PERSIST)

    else:
        # Hold Shoulder Stepper at desired Position.
        GPIO.output(out[1], GPIO.LOW)

def setup_logfile(name):
    """Create File for data logging.

    This function creates a CSV file, appends the current date to the
    filename, and opens the file for data recording.

    Args:
        name:       A String specifying the desired file name. The current
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
        pin:        A String specifying the pin name on which the 
                    pressure sensor signal is expected.

    Returns:
        __diff:     The calculated pressure difference [psi].
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
        pin:        A String specifying the pin name on which the 
                    pressure sensor signal is excepted.
        freq:       An Integer specifying the desired logging 
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
