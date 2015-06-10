# -*- coding: utf-8 -*-
#   AndoriDus - A Python wrapper for Andor's scientific cameras
#
#   Original code by
#   Copyright (C) 2009  Hamid Ohadi
#
#   Adapted for iDus, qtlab and Windows XP
#   2010 Martijn Schaafsma
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
This module offers basic functionality for the Andor iDus ans iXon
'''

# Modules for Andor functionality
from ctypes import windll, c_int, c_char, byref, c_long, \
    pointer, c_float, c_char_p, cdll
from PIL import Image
import sys
import time
import platform
import os

#class AndorIdus(Instrument):
class AndorIdus():
    """
    Andor class which is meant to provide the Python version of the same
    functions that are defined in the Andor's SDK. Extensive documentation
    on the functions used and error codes can be
    found in the Andor SDK Users Guide
    """
    def __init__(self):
        '''
        Loads and initializes the hardware driver.
        Initializes local parameters

        Input:
            name (string)   : The name of the device
        '''

        # Check operating system and load library
        if platform.system() == "Linux":
            dllname = "/usr/local/lib/libandor.so"
            self._dll = cdll.LoadLibrary(dllname)
        elif platform.system() == "Windows":
            dllname = "C:\\Program Files\\Andor iDus\\ATMCD32D"
            self._dll = windll.LoadLibrary(dllname)
        else:
            print "Cannot detect operating system, wil now stop"
            raise

        # Initialize the device
        tekst = c_char()
        error = self._dll.Initialize(byref(tekst))
        print "Initializing: %s" % ( ERROR_CODE[error])

        cw = c_int()
        ch = c_int()
        self._dll.GetDetector(byref(cw), byref(ch))

        # Initiate parameters
        self._width        = cw.value
        self._height       = ch.value
        self._temperature  = None
        self._set_T        = None
        self._gain         = None
        self._gainRange    = None
        self._status       = ERROR_CODE[error]
        self._verbosity    = True
        self._preampgain   = None
        self._channel      = None
        self._outamp       = None
        self._hsspeed      = None
        self._vsspeed      = None
        self._serial       = None
        self._exposure     = None
        self._accumulate   = None
        self._kinetic      = None
        self._bitDepths    = []
        self._preAmpGain   = []
        self._VSSpeeds     = []
        self._noGains      = None
        self._imageArray   = []
        self._noVSSpeeds   = None
        self._HSSpeeds     = []
        self._noADChannels = None
        self._noHSSpeeds   = None
        self._ReadMode     = None


    def __del__(self):
       error = self._dll.ShutDown()
       self._Verbose(ERROR_CODE[error] )

    def LINE( self, back = 0 ):
        '''
        Return line of statement in code

        Input:
            back (int)   : The number of positions to move
                           up in the calling stack (default=0)

        Output:
            (string)     : The requested information
        '''
        return sys._getframe( back + 1 ).f_lineno

    def FILE( self, back = 0 ):
        '''
        Return filename of source code

        Input:
            back (int)   : The number of positions to move
                           up in the calling stack (default=0)

        Output:
            (string)     : The requested information
        '''
        return sys._getframe( back + 1 ).f_code.co_filename

    def FUNC( self, back = 0):
        '''
        Return function name

        Input:
            back (int)   : The number of positions to move
                           up in the calling stack (default=0)

        Output:
            (string)     : The requested information
        '''
        return sys._getframe( back + 1 ).f_code.co_name

    def WHERE( self, back = 0 ):
        '''
        Return information of location of calling function

        Input:
            back (int)   : The number of positions to move
                           up in the calling stack (default=0)

        Output:
            (string)     : The requested information
        '''
        frame = sys._getframe( back + 1 )
        return "%s/%s %s()" % ( os.path.basename( frame.f_code.co_filename ),
                                frame.f_lineno, frame.f_code.co_name )

    def _Verbose(self, error):
        '''
        Reports all error codes to stdout if self._verbosity=True

        Input:
            error (string)  : The string resulted from the error code
            name (string)   : The name of the function calling the device

        Output:
            None
        '''
        if self._verbosity is True:
            print "[%s]: %s" % (self.FUNC(1), error)

    def SetVerbose(self, state=True):
        '''
        Enable / disable printing error codes to stdout

        Input:
            state (bool)  : toggle verbosity, default=True

        Output:
            None
        '''
        self._verbosity = state

# Get Camera properties

    def GetCameraSerialNumber(self):
        '''
        Returns the serial number of the camera

        Input:
            None

        Output:
            (int) : Serial number of the camera
        '''
        serial = c_int()
        error = self._dll.GetCameraSerialNumber(byref(serial))
        self._serial = serial.value
        self._Verbose(ERROR_CODE[error] )
        return self._serial

    def GetNumberHSSpeeds(self):
        '''
        Returns the number of HS speeds

        Input:
            None

        Output:
            (int) : the number of HS speeds
        '''
        noHSSpeeds = c_int()
        error = self._dll.GetNumberHSSpeeds(self._channel, self._outamp,
                                            byref(noHSSpeeds))
        self._noHSSpeeds = noHSSpeeds.value
        self._Verbose(ERROR_CODE[error] )
        return self._noHSSpeeds

    def GetNumberVSSpeeds(self):
        '''
        Returns the number of VS speeds

        Input:
            None

        Output:
            (int) : the number of VS speeds
        '''
        noVSSpeeds = c_int()
        error = self._dll.GetNumberVSSpeeds(byref(noVSSpeeds))
        self._noVSSpeeds = noVSSpeeds.value
        self._Verbose(ERROR_CODE[error] )
        return self._noVSSpeeds

# Cooler and temperature
    def CoolerON(self):
        '''
        Switches the cooler on

        Input:
            None

        Output:
            None
        '''
        error = self._dll.CoolerON()
        self._Verbose(ERROR_CODE[error])

    def CoolerOFF(self):
        '''
        Switches the cooler off

        Input:
            None

        Output:
            None
        '''
        error = self._dll.CoolerOFF()
        self._Verbose(ERROR_CODE[error])

    def SetCoolerMode(self, mode):
        '''
        Set the cooler mode

        Input:
            mode (int) : cooler modus

        Output:
            None
        '''
        error = self._dll.SetCoolerMode(mode)
        self._Verbose(ERROR_CODE[error] )

    def IsCoolerOn(self):
        '''
        Returns cooler status

        Input:
            None

        Output:
            (int) : Cooler status
        '''
        iCoolerStatus = c_int()
        error = self._dll.IsCoolerOn(byref(iCoolerStatus))
        self._Verbose(ERROR_CODE[error] )
        return iCoolerStatus.value

    def GetTemperature(self):
        '''
        Returns the temperature in degrees Celcius

        Input:
            None

        Output:
            (int) : temperature in degrees Celcius
        '''
        ctemperature = c_int()
        error = self._dll.GetTemperature(byref(ctemperature))
        self._temperature = ctemperature.value
        self._Verbose(ERROR_CODE[error] )
        print "Temperature is: %g [Set T: %g]" \
            % (self._temperature, self._set_T)
        return ERROR_CODE[error]

    def SetTemperature(self, temperature): # Fixme:, see if this works
        '''
        Set the working temperature of the camera

        Input:
            temparature (int) : temperature in degrees Celcius

        Output:
            None
        '''
#        ctemperature = c_int(temperature)
        error = self._dll.SetTemperature(temperature)
        self._set_T = temperature
        self._Verbose(ERROR_CODE[error] )


###### Single Parameters Set ######
    def SetAccumulationCycleTime(self, time_):
        '''
        Set the accumulation cycle time

        Input:
            time_ (float) : the accumulation cycle time in seconds

        Output:
            None
        '''
        error = self._dll.SetAccumulationCycleTime(c_float(time_))
        self._Verbose(ERROR_CODE[error] )

    def SetAcquisitionMode(self, mode):
        '''
        Set the acquisition mode of the camera

        Input:
            mode (int) : acquisition mode

        Output:
            None
        '''
        error = self._dll.SetAcquisitionMode(mode)
        self._Verbose(ERROR_CODE[error] )

    def SetADChannel(self, index):
        '''
        Set the A-D channel for acquisition

        Input:
            index (int) : AD channel

        Output:
            None
        '''
        error = self._dll.SetADChannel(index)
        self._Verbose(ERROR_CODE[error] )
        self._channel = index

    def SetEMAdvanced(self, gainAdvanced):
        '''
        Enable/disable access to the advanced EM gain levels

        Input:
            gainAdvanced (int) : 1 or 0 for true or false

        Output:
            None
        '''
        error = self._dll.SetEMAdvanced(gainAdvanced)
        self._Verbose(ERROR_CODE[error] )

    def SetEMCCDGainMode(self, gainMode):
        '''
        Set the gain mode

        Input:
            gainMode (int) : mode

        Output:
            None
        '''
        error = self._dll.SetEMCCDGainMode(gainMode)
        self._Verbose(ERROR_CODE[error] )

    def SetExposureTime(self, time_):
        '''
        Set the exposure time in seconds

        Input:
            time_ (float) : The exposure time in seconds

        Output:
            None
        '''
        error = self._dll.SetExposureTime(c_float(time_))
        self._Verbose(ERROR_CODE[error] )

    def SetFrameTransferMode(self, frameTransfer):
        '''
        Enable/disable the frame transfer mode

        Input:
            frameTransfer (int) : 1 or 0 for true or false

        Output:
            None
        '''
        error = self._dll.SetFrameTransferMode(frameTransfer)
        self._Verbose(ERROR_CODE[error] )

    def SetImageRotate(self, iRotate):
        '''
        Set the modus for image rotation

        Input:
            iRotate (int) : 0 for no rotation, 1 for 90 deg cw, 2 for 90 deg ccw

        Output:
            None
        '''
        error = self._dll.SetImageRotate(iRotate)
        self._Verbose(ERROR_CODE[error] )

    def SetKineticCycleTime(self, time_):
        '''
        Set the Kinetic cycle time in seconds

        Input:
            time_ (float) : The cycle time in seconds

        Output:
            None
        '''
        error = self._dll.SetKineticCycleTime(c_float(time_))
        self._Verbose(ERROR_CODE[error] )

    def SetNumberAccumulations(self, number):
        '''
        Set the number of scans accumulated in memory,
        for kinetic and accumulate modes

        Input:
            number (int) : The number of accumulations

        Output:
            None
        '''
        error = self._dll.SetNumberAccumulations(number)
        self._Verbose(ERROR_CODE[error] )

    def SetNumberKinetics(self, numKin):
        '''
        Set the number of scans accumulated in memory for kinetic mode

        Input:
            number (int) : The number of accumulations

        Output:
            None
        '''
        error = self._dll.SetNumberKinetics(numKin)
        self._Verbose(ERROR_CODE[error] )

    def SetOutputAmplifier(self, index):
        '''
        Specify which amplifier to use if EMCCD is enabled

        Input:
            index (int) : 0 for EMCCD, 1 for conventional

        Output:
            None
        '''
        error = self._dll.SetOutputAmplifier(index)
        self._Verbose(ERROR_CODE[error] )
        self._outamp = index

    def SetReadMode(self, mode):
        '''
        Set the read mode of the camera

        Input:
            mode (int) : 0 Full Vertical Binning
                         1 Multi-Track
                         2 Random-track
                         3 Single-Track
                         4 Image

        Output:
            None
        '''
        error = self._dll.SetReadMode(mode)
        self._ReadMode = mode
        self._Verbose(ERROR_CODE[error] )

    def SetTriggerMode(self, mode):
        '''
        Set the trigger mode

        Input:
            mode (int) : 0 Internal
                         1 External
                         2 External Start (only in Fast Kinetics mode)

        Output:
            None
        '''
        error = self._dll.SetTriggerMode(mode)
        self._Verbose(ERROR_CODE[error] )


###### Single Parameters Get ######

    def GetAccumulationProgress(self):
        '''
        Returns the number of completed accumulations

        Input:
            None

        Output:
            (int) : The number of accumulations
        '''
        acc = c_long()
        series = c_long()
        error = self._dll.GetAcquisitionProgress(byref(acc), byref(series))
        if ERROR_CODE[error] == "DRV_SUCCESS":
            return acc.value
        else:
            return None

    def GetAcquiredData(self, imageArray):
        '''
        Returns the Acquired data

        Input:
            None

        Output:
            (array) : an array containing the acquired data
        '''
        # FIXME : Check how this works for FVB !!!
        if self._ReadMode == 0:
            dim = self._width
        elif self._ReadMode == 4:
            dim = self._width * self._height
            
        print "Dim is %s" % dim
        cimageArray = c_int * dim
        cimage = cimageArray()
        error = self._dll.GetAcquiredData(pointer(cimage), dim)
        self._Verbose(ERROR_CODE[error] )

        for i in range(len(cimage)):
            imageArray.append(cimage[i])

        self._imageArray = imageArray[:]
        self._Verbose(ERROR_CODE[error] )
        return self._imageArray

    def GetBitDepth(self):
        '''
        Returns the bit depth of the available channels

        Input:
            None

        Output:
            (int[]) : The bit depths
        '''
        bitDepth = c_int()
        self._bitDepths = []

        for i in range(self._noADChannels):
            self._dll.GetBitDepth(i, byref(bitDepth))
            self._bitDepths.append(bitDepth.value)
        return self._bitDepths

    def GetEMGainRange(self):
        '''
        Returns the number of completed accumulations

        Input:
            None

        Output:
            int) : The number of accumulations
        '''
        low = c_int()
        high = c_int()
        error = self._dll.GetEMGainRange(byref(low), byref(high))
        self._gainRange = (low.value, high.value)
        self._Verbose(ERROR_CODE[error] )
        return self._gainRange

    def GetNumberADChannels(self):
        '''
        Returns the number of AD channels

        Input:
            None

        Output:
            (int) : The number of AD channels
        '''
        noADChannels = c_int()
        error = self._dll.GetNumberADChannels(byref(noADChannels))
        self._noADChannels = noADChannels.value
        self._Verbose(ERROR_CODE[error] )
        return self._noADChannels

    def GetNumberPreAmpGains(self):
        '''
        Returns the number of Pre Amp Gains

        Input:
            None

        Output:
            (int) : The number of Pre Amp Gains
        '''
        noGains = c_int()
        error = self._dll.GetNumberPreAmpGains(byref(noGains))
        self._noGains = noGains.value
        self._Verbose(ERROR_CODE[error] )
        return self._noGains

    def GetSeriesProgress(self):
        '''
        Returns the number of completed kenetic scans

        Input:
            None

        Output:
            (int) : The number of completed kinetic scans
        '''
        acc = c_long()
        series = c_long()
        error = self._dll.GetAcquisitionProgress(byref(acc), byref(series))
        if ERROR_CODE[error] == "DRV_SUCCESS":
            return series.value
        else:
            return None

    def GetStatus(self):
        '''
        Returns the status of the camera

        Input:
            None

        Output:
            (string) : DRV_IDLE
                       DRV_TEMPCYCLE
                       DRV_ACQUIRING
                       DRV_TIME_NOT_MET
                       DRV_KINETIC_TIME_NOT_MET
                       DRV_ERROR_ACK
                       DRV_ACQ_BUFFER
                       DRV_SPOOLERROR
        '''
        status = c_int()
        error = self._dll.GetStatus(byref(status))
        self._status = ERROR_CODE[status.value]
        self._Verbose(ERROR_CODE[error] )
        return self._status

###### Single Parameters Get/Set ######
    def GetEMCCDGain(self):
        '''
        Returns EMCCD Gain setting

        Input:
            None

        Output:
            (int) : EMCCD gain setting
        '''
        gain = c_int()
        error = self._dll.GetEMCCDGain(byref(gain))
        self._gain = gain.value
        self._Verbose(ERROR_CODE[error] )
        return self._gain

    def SetEMCCDGain(self, gain):
        '''
        Set the EMCCD Gain setting

        Input:
            gain (int) : EMCCD setting

        Output:
            None
        '''
        error = self._dll.SetEMCCDGain(gain)
        self._Verbose(ERROR_CODE[error] )

    def GetHSSpeed(self):
        '''
        Returns the available HS speeds of the selected channel

        Input:
            None

        Output:
            (float[]) : The speeds of the selected channel
        '''
        HSSpeed = c_float()
        self._HSSpeeds = []
        for i in range(self._noHSSpeeds):
            self._dll.GetHSSpeed(self._channel, self._outamp, i, byref(HSSpeed))
            self._HSSpeeds.append(HSSpeed.value)
        return self._HSSpeeds

    def SetHSSpeed(self, index):
        '''
        Set the HS speed to the mode corresponding to the index

        Input:
            index (int) : index corresponding to the Speed mode

        Output:
            None
        '''
        error = self._dll.SetHSSpeed(index)
        self._Verbose(ERROR_CODE[error] )
        self._hsspeed = index

    def GetVSSpeed(self):
        '''
        Returns the available VS speeds of the selected channel

        Input:
            None

        Output:
            (float[]) : The speeds of the selected channel
        '''
        VSSpeed = c_float()
        self._VSSpeeds = []

        for i in range(self._noVSSpeeds):
            self._dll.GetVSSpeed(i, byref(VSSpeed))
            self._VSSpeeds.append(VSSpeed.value)
        return self._VSSpeeds

    def SetVSSpeed(self, index):
        '''
        Set the VS speed to the mode corresponding to the index

        Input:
            index (int) : index corresponding to the Speed mode

        Output:
            None
        '''
        error = self._dll.SetVSSpeed(index)
        self._Verbose(ERROR_CODE[error] )
        self._vsspeed = index

    def GetPreAmpGain(self):
        '''
        Returns the available Pre Amp Gains

        Input:
            None

        Output:
            (float[]) : The pre amp gains
        '''
        gain = c_float()
        self._preAmpGain = []

        for i in range(self._noGains):
            self._dll.GetPreAmpGain(i, byref(gain))
            self._preAmpGain.append(gain.value)
        return self._preAmpGain

    def SetPreAmpGain(self, index):
        '''
        Set the Pre Amp Gain to the mode corresponding to the index

        Input:
            index (int) : index corresponding to the Gain mode

        Output:
            None
        '''
        error = self._dll.SetPreAmpGain(index)
        self._Verbose(ERROR_CODE[error] )
        self._preampgain = index


###### iDus interaction Functions ######
    def ShutDown(self): # Careful with this one!!
        '''
        Shut down the Andor
        '''
        error = self._dll.ShutDown()
        self._Verbose(ERROR_CODE[error] )

    def AbortAcquisition(self):
        '''
        Abort the acquisition
        '''
        error = self._dll.AbortAcquisition()
        self._Verbose(ERROR_CODE[error] )

    def StartAcquisition(self):
        '''
        Start the acquisition
        '''
        error = self._dll.StartAcquisition()
        #self._dll.WaitForAcquisition()
        self._Verbose(ERROR_CODE[error] )

    def SetSingleImage(self):
        '''
        Shortcut to apply settings for a single scan full image
        '''
        self.SetReadMode(4)
        self.SetAcquisitionMode(1)
        print "Width: %d Height: %d" % (self._width, self._height)
        self.SetImage(1, 1, 1, self._width, 1, self._height)

    def SetSingleFVB(self):
        '''
        Shortcut to apply settings for a single scan FVB
        '''
        self.SetReadMode(0)
        self.SetAcquisitionMode(1)

    def GetAcquisitionTimings(self):
        '''
        Acquire all the relevant timings for acquisition,
        and store them in local memory
        '''
        exposure   = c_float()
        accumulate = c_float()
        kinetic    = c_float()
        error = self._dll.GetAcquisitionTimings(byref(exposure),
                                            byref(accumulate),byref(kinetic))
        self._exposure = exposure.value
        self._accumulate = accumulate.value
        self._kinetic = kinetic.value
        self._Verbose(ERROR_CODE[error] )


###### Misc functions ######

    def SetImage(self, hbin, vbin, hstart, hend, vstart, vend):
        '''
        Specify the binning and domain of the image

        Input:
            hbin   (int) : horizontal binning
            vbin   (int) : vertical binning
            hstart (int) : horizontal starting point
            hend   (int) : horizontal end point
            vstart (int) : vertical starting point
            vend   (int) : vertical end point

        Output:
            None
        '''
        error = self._dll.SetImage(hbin, vbin, hstart, hend, vstart, vend)
        self._Verbose(ERROR_CODE[error] )

    def SetShutter(self, typ, mode, closingtime, openingtime):
        '''
        Set the configuration for the shutter

        Input:
            typ         (int) : 0/1 Output TTL low/high signal to open shutter
            mode        (int) : 0/1/2 For Auto/Open/Close
            closingtime (int) : millisecs it takes to close
            openingtime (int) : millisecs it takes to open

        Output:
            None
        '''
        error = self._dll.SetShutter(typ, mode, closingtime, openingtime)
        self._Verbose(ERROR_CODE[error] )

    def SetShutterEx(self, typ, mode, closingtime, openingtime, extmode):
        '''
        Set the configuration for the shutter in external mode

        Input:
            typ         (int) : 0/1 Output TTL low/high signal to open shutter
            mode        (int) : 0/1/2 For Auto/Open/Close
            closingtime (int) : millisecs it takes to close
            openingtime (int) : millisecs it takes to open
            extmode     (int) : 0/1/2 For Auto/Open/Close

        Output:
            None
        '''
        error = self._dll.SetShutterEx(typ, mode, closingtime, openingtime,
                                       extmode)
        self._Verbose(ERROR_CODE[error] )

    def SetSpool(self, active, method, path, framebuffersize):
        '''
        Set Spooling. Refer to manual for detailed description
        '''
        error = self._dll.SetSpool(active, method, c_char_p(path),
                                   framebuffersize)
        self._Verbose(ERROR_CODE[error] )

    def SaveAsBmp(self, path):
        '''
        Save the most recent acquired image as a bitmap

        Input:
            path (string) : Filename to save to

        Output:
            None
        '''
        im = Image.new("RGB", (self._height, self._width), "white")
        pix = im.load()

        for i in range(len(self._imageArray)):
            (row, col) = divmod(i, self._width)
            picvalue = int(round(self._imageArray[i]*255.0/65535))
            pix[row, col] = (picvalue, picvalue, picvalue)

        im.save(path,"BMP")

    def SaveAsTxt(self, path):
        '''
        Save the most recent acquired image as txt

        Input:
            path (string) : Filename to save to

        Output:
            None
        '''
        filename = open(path, 'w')

        for line in self._imageArray:
            filename.write("%g\n" % line)
        filename.close()

    def SaveAsBmpNormalised(self, path):
        '''
        Save the most recent acquired image as a bitmap,
        but maximize contrast

        Input:
            path (string) : Filename to save to

        Output:
            None
        '''
        im = Image.new("RGB", (self._height, self._width),"white")
        pix = im.load()
        maxIntensity = max(self._imageArray)
        minIntensity = min(self._imageArray)
        print maxIntensity, minIntensity
        for i in range(len(self._imageArray)):
            (row, col) = divmod(i, self._width)
            picvalue = int(round((self._imageArray[i]-minIntensity)*255.0/
                (maxIntensity-minIntensity)))
            pix[row, col] = (picvalue, picvalue, picvalue)
        im.save(path, "BMP")

    def SaveAsFITS(self, filename, type_):
        '''
        Save the most recent acquired image as FITS

        Input:
            path (string) : Filename to save to

        Output:
            None
        '''
        error = self._dll.SaveAsFITS(filename, type_)
        self._Verbose(ERROR_CODE[error] )


########### Automation functions #################

    def Demo_CoolDown(self):
        '''
        Cool down the camera for a demo measurement
        '''
        Tset = -25
        self.SetCoolerMode(1)

        self.SetTemperature(Tset)
        self.CoolerON()

        while self.GetTemperature() is not 'DRV_TEMP_STABILIZED':
            time.sleep(10)

    def Demo_ImagePrepare(self):
        '''
        Prepare the camera for a demo image measurement
        '''
        PreAmpGain = 0
        self.SetSingleImage()
        self.SetTriggerMode(0)
        self.SetShutter(1, 1, 0, 0)
        self.SetPreAmpGain(PreAmpGain)
        self.SetExposureTime(0.1)

    def Demo_ImageCapture(self):
        '''
        Perform the demo image measurement
        '''
        i = 0
        while i < 4:
            i += 1
            print self.GetTemperature()
            print self._temperature
            print "Ready for Acquisition"
            self.StartAcquisition()

            # Check for status
            while self.GetStatus() is not 'DRV_IDLE':
                print "Data not yet acquired, waiting 0.5s"
                time.sleep(0.5)

            data = []
            self.GetAcquiredData(data)
            self.SaveAsBmpNormalised("n%03g.bmp" % i)
            self.SaveAsBmp("%03g.bmp" % i)
            self.SaveAsTxt("%03g.txt" % i)

    def Demo_FVBPrepare(self):
        '''
        Prepare the camera for a demo image measurement
        '''
        PreAmpGain = 0
        self.SetSingleFVB()
        self.SetTriggerMode(0)
        self.SetShutter(1, 1, 0, 0)
        self.SetPreAmpGain(PreAmpGain)
        self.SetExposureTime(0.1)

    def Demo_FVBCapture(self):
        '''
        Perform the demo image measurement
        '''
        i = 0
        while i < 4:
            i += 1
            print self.GetTemperature()
            print self._temperature
            print "Ready for Acquisition"
            self.StartAcquisition()

            # Check for status
            while self.GetStatus() is not 'DRV_IDLE':
                print "Data not yet acquired, waiting 0.5s"
                time.sleep(0.5)

            data = []
            self.GetAcquiredData(data)
            self.SaveAsTxt("%03g.txt" % i)

#####################################################

# List of error codes
ERROR_CODE = {
    20001: "DRV_ERROR_CODES",
    20002: "DRV_SUCCESS",
    20003: "DRV_VXNOTINSTALLED",
    20006: "DRV_ERROR_FILELOAD",
    20007: "DRV_ERROR_VXD_INIT",
    20010: "DRV_ERROR_PAGELOCK",
    20011: "DRV_ERROR_PAGE_UNLOCK",
    20013: "DRV_ERROR_ACK",
    20024: "DRV_NO_NEW_DATA",
    20026: "DRV_SPOOLERROR",
    20034: "DRV_TEMP_OFF",
    20035: "DRV_TEMP_NOT_STABILIZED",
    20036: "DRV_TEMP_STABILIZED",
    20037: "DRV_TEMP_NOT_REACHED",
    20038: "DRV_TEMP_OUT_RANGE",
    20039: "DRV_TEMP_NOT_SUPPORTED",
    20040: "DRV_TEMP_DRIFT",
    20050: "DRV_COF_NOTLOADED",
    20053: "DRV_FLEXERROR",
    20066: "DRV_P1INVALID",
    20067: "DRV_P2INVALID",
    20068: "DRV_P3INVALID",
    20069: "DRV_P4INVALID",
    20070: "DRV_INIERROR",
    20071: "DRV_COERROR",
    20072: "DRV_ACQUIRING",
    20073: "DRV_IDLE",
    20074: "DRV_TEMPCYCLE",
    20075: "DRV_NOT_INITIALIZED",
    20076: "DRV_P5INVALID",
    20077: "DRV_P6INVALID",
    20083: "P7_INVALID",
    20089: "DRV_USBERROR",
    20091: "DRV_NOT_SUPPORTED",
    20099: "DRV_BINNING_ERROR",
    20990: "DRV_NOCAMERA",
    20991: "DRV_NOT_SUPPORTED",
    20992: "DRV_NOT_AVAILABLE"
}