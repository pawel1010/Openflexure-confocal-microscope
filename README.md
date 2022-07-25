# Openflexure-confocal-microscope

I'm to building the confocal microscope using OpenFlexure Delta Stage project. I wanted to use a microscope with a program in python which consists of three parts:

- main.py: the script that executes the XYZ scan.  Runs on the PC, talks to the RPi which is controlling the OpenFlexure stage
- stage.py: a plugin that was added to the OpenFlexure server code.  This exposes a "moveMeasure" API which commands the stage to move to a position and then read the ADC (which is reading the photodiode, it's ADS 1115 communicating via i2c).
- imageStack.py: The script that processed the raw photodiode data into an image. Various methods of processing commented out.
- image.py: Current candidate for working version of imageStack.py
