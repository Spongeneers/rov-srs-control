# rov-srs-control

Control Software/Scripts for a Sample Retrieval System attached to a deep-sea ROV.


This repository contains the Python Scripts used to control a robotic arm attached to a deep-sea ROV.
This arm is used to collect samples of sponge lifeforms (hence the name Sample Retrieval System, or SRS).
The arm achieves this functionality via input from a standard RC Controller and output to 3 actuators
(1 Linear, 2 Steppers).

The project includes 2 major scripts, both intended to be run on a BeagleBone Black Rev C
(and both dependent on the "Adafruit_BBIO" Python library. The scripts are as follows:
    ROV_SRS_Library.py: Library containing all sub-functions used during control processes.
    ROV_SRS_Main.py:    Main script run automatically during ROV operation.

In addition to these scripts, this repository includes the design documentation used to arrive
at this program architecture (located in the "doc" sub-directory).
