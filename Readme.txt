This is a small Python wrapper for Andor cameras and spectrometers. It tries to stick to the same function naming that Andor does. Therefore, it should be fairly trivial how to use it.
The module is object oriented and keeps some information inside the class such as gain, preampgain, gainRange etc.

The main modules is 'andor.py'. This module has been tested both in Windows and Linux with Newton and EM ranges from Andor. There is another module which has been tested on Windows for iDus range.

Simple example:


import pyandor

cam = Andor()
cam.SetDemoReady()
cam.StartAcquisition()
data = []
cam.GetAcquiredData(data)
cam.SaveAsTxt("raw.txt")
cam.ShutDown()
