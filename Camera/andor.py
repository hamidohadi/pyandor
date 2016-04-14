#   pyAndor - A Python wrapper for Andor's scientific cameras
#   Copyright (C) 2009  Hamid Ohadi
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

import platform
from ctypes import *
from PIL import Image
import sys

"""Andor class which is meant to provide the Python version of the same
   functions that are defined in the Andor's SDK. Since Python does not
   have pass by reference for immutable variables, some of these variables
   are actually stored in the class instance. For example the temperature,
   gain, gainRange, status etc. are stored in the class. """

class Andor:
    def __init__(self):

        # Check operating system and load library
        # for Windows
        if platform.system() == "Windows":
            if platform.architecture()[0] == "32bit":
                self.dll = cdll("C:\\Program Files\\Andor SOLIS\\Drivers\\atmcd32d")
            else:
                self.dll = cdll("C:\\Program Files\\Andor SOLIS\\Drivers\\atmcd64d")
        # for Linux
        if platform.system() == "Linux":
            dllname = "/usr/local/lib/libandor.so"
            self.dll = cdll.LoadLibrary(dllname)
        else:
            print "Cannot detect operating system, wil now stop"
            raise

        self.Initialize()

        cw = c_int()
        ch = c_int()
        self.dll.GetDetector(byref(cw), byref(ch))
   
    
        self.width       = cw.value
        self.height      = ch.value
        self.temperature = None
        self.set_T       = None
        self.gain        = None
        self.gainRange   = None
        self.status      = ERROR_CODE[error]
        self.verbosity   = True
        self.preampgain  = None
        self.channel     = None
        self.outamp      = None
        self.hsspeed     = None
        self.vsspeed     = None
        self.serial      = None
        self.exposure    = None
        self.accumulate  = None
        self.kinetic     = None
        self.ReadMode    = None
        self.AcquisitionMode = None
        self.scans       = 1
        self.hbin        = 1
        self.vbin        = 1
        self.hstart      = 1
        self.hend        = cw
        self.vstart      = 1
        self.vend        = ch
        self.cooler      = None
        
    def __del__(self):
        error = self.dll.ShutDown()
    
    def verbose(self, error, function=''):
        if self.verbosity is True:
            print "[%s]: %s" %(function, error)

    def SetVerbose(self, state=True):
        self.verbose = state

    def AbortAcquisition(self):
        error = self.dll.AbortAcquisition()
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def Initialize(self):
        tekst = c_char()  
        error = self.dll.Initialize(byref(tekst))
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]
        
    def ShutDown(self):
        error = self.dll.ShutDown()
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]
        
    def GetCameraSerialNumber(self):
        serial = c_int()
        error = self.dll.GetCameraSerialNumber(byref(serial))
        self.serial = serial.value
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def SetReadMode(self, mode):
        #0: Full vertical binning
        #1: multi track
        #2: random track
        #3: single track
        #4: image
        error = self.dll.SetReadMode(mode)
        self.ReadMode = mode
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def SetAcquisitionMode(self, mode):
        #1: Single scan
        #3: Kinetic scan
        error = self.dll.SetAcquisitionMode(mode)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        self.AcquisitionMode = mode
        return ERROR_CODE[error]
        
    def SetNumberKinetics(self,numKin):
        error = self.dll.SetNumberKinetics(numKin)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        self.scans = numKin
        return ERROR_CODE[error]

    def SetNumberAccumulations(self,number):
        error = self.dll.SetNumberAccumulations(number)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def SetAccumulationCycleTime(self,time):
        error = self.dll.SetAccumulationCycleTime(c_float(time))
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def SetKineticCycleTime(self,time):
        error = self.dll.SetKineticCycleTime(c_float(time))
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def SetShutter(self,typ,mode,closingtime,openingtime):
        error = self.dll.SetShutter(typ,mode,closingtime,openingtime)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def SetImage(self,hbin,vbin,hstart,hend,vstart,vend):
        self.hbin = hbin
        self.vbin = vbin
        self.hstart = hstart
        self.hend = hend
        self.vstart = vstart
        self.vend = vend
        
        error = self.dll.SetImage(hbin,vbin,hstart,hend,vstart,vend)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def StartAcquisition(self):
        error = self.dll.StartAcquisition()
        self.dll.WaitForAcquisition()
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def GetAcquiredData(self,imageArray):
        if (self.ReadMode==4):
            if (self.AcquisitionMode==1):
                dim = self.width * self.height / self.hbin / self.vbin
            elif (self.AcquisitionMode==3):
                dim = self.width * self.height / self.hbin / self.vbin * self.scans
        elif (self.ReadMode==3 or self.ReadMode==0):
            if (self.AcquisitionMode==1):
                dim = self.width
            elif (self.AcquisitionMode==3):
                dim = self.width * self.scans

        cimageArray = c_int * dim
        cimage = cimageArray()
        error = self.dll.GetAcquiredData(pointer(cimage),dim)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)

        for i in range(len(cimage)):
            imageArray.append(cimage[i])

        self.imageArray = imageArray[:]
        #self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def SetExposureTime(self, time):
        error = self.dll.SetExposureTime(c_float(time))
        self.exposure = time
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]
        
    def GetAcquisitionTimings(self):
        exposure   = c_float()
        accumulate = c_float()
        kinetic    = c_float()
        error = self.dll.GetAcquisitionTimings(byref(exposure),byref(accumulate),byref(kinetic))
        self.exposure = exposure.value
        self.accumulate = accumulate.value
        self.kinetic = kinetic.value
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def SetSingleScan(self):
        self.SetReadMode(4)
        self.SetAcquisitionMode(1)
        self.SetImage(1,1,1,self.width,1,self.height)

    def SetCoolerMode(self, mode):
        error = self.dll.SetCoolerMode(mode)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]
        
    def SetFanMode(self, mode):
        #0: fan on full
        #1: fan on low
        #2: fna off
        error = self.dll.SetFanMode(mode)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def SaveAsBmp(self, path):
        im=Image.new("RGB",(self.width,self.height),"white")
        pix = im.load()

        for i in range(len(self.imageArray)):
            (row, col) = divmod(i,self.width)
            picvalue = int(round(self.imageArray[i]*255.0/65535))
            pix[col,row] = (picvalue,picvalue,picvalue)

        im.save(path,"BMP")

    def SaveAsTxt(self, path):
        file = open(path, 'w')

        for line in self.imageArray:
            file.write("%g\n" % line)

        file.close()

    def SetImageRotate(self, iRotate):
        error = self.dll.SetImageRotate(iRotate)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)

    def SaveAsBmpNormalised(self, path):

        im=Image.new("RGB",(self.width,self.height),"white")
        pix = im.load()

        maxIntensity = max(self.imageArray)

        for i in range(len(self.imageArray)):
            (row, col) = divmod(i,self.width)
            picvalue = int(round(self.imageArray[i]*255.0/maxIntensity))
            pix[col,row] = (picvalue,picvalue,picvalue)

        im.save(path,"BMP")
        
    def SaveAsFITS(self, filename, type):
		error = self.dll.SaveAsFITS(filename, type)
		self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
		return ERROR_CODE[error]

    def CoolerON(self):
        error = self.dll.CoolerON()
        self.cooler = 1
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def CoolerOFF(self):
        error = self.dll.CoolerOFF()
        self.cooler = 0
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def IsCoolerOn(self):
        iCoolerStatus = c_int()
        self.cooler = iCoolerStatus
        error = self.dll.IsCoolerOn(byref(iCoolerStatus))
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return iCoolerStatus.value

    def GetTemperature(self):
        ctemperature = c_int()
        error = self.dll.GetTemperature(byref(ctemperature))
        self.temperature = ctemperature.value
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def SetTemperature(self,temperature):
        #ctemperature = c_int(temperature)
        #error = self.dll.SetTemperature(byref(ctemperature))
        error = self.dll.SetTemperature(temperature)
        self.set_T = temperature
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def GetEMCCDGain(self):
        gain = c_int()
        error = self.dll.GetEMCCDGain(byref(gain))
        self.gain = gain.value
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]
     
    def SetEMCCDGainMode(self, gainMode):
        error = self.dll.SetEMCCDGainMode(gainMode)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]   
        
    def SetEMCCDGain(self, gain):
        error = self.dll.SetEMCCDGain(gain)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]
        
    def SetEMAdvanced(self, gainAdvanced):
		error = self.dll.SetEMAdvanced(gainAdvanced)
		self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
		return ERROR_CODE[error]

    def GetEMGainRange(self):
        low = c_int()
        high = c_int()
        error = self.dll.GetEMGainRange(byref(low),byref(high))
        self.gainRange = (low.value, high.value)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]
      
    def GetNumberADChannels(self):
        noADChannels = c_int()
        error = self.dll.GetNumberADChannels(byref(noADChannels))
        self.noADChannels = noADChannels.value
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def GetBitDepth(self):
        bitDepth = c_int()

        self.bitDepths = []

        for i in range(self.noADChannels):
            self.dll.GetBitDepth(i,byref(bitDepth))
            self.bitDepths.append(bitDepth.value)

    def SetADChannel(self, index):
        error = self.dll.SetADChannel(index)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        self.channel = index
        return ERROR_CODE[error]  
        
    def SetOutputAmplifier(self, index):
        error = self.dll.SetOutputAmplifier(index)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        self.outamp = index
        return ERROR_CODE[error]
        
    def GetNumberHSSpeeds(self):
        noHSSpeeds = c_int()
        error = self.dll.GetNumberHSSpeeds(self.channel, self.outamp, byref(noHSSpeeds))
        self.noHSSpeeds = noHSSpeeds.value
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def GetHSSpeed(self):
        HSSpeed = c_float()

        self.HSSpeeds = []

        for i in range(self.noHSSpeeds):
            self.dll.GetHSSpeed(self.channel, self.outamp, i, byref(HSSpeed))
            self.HSSpeeds.append(HSSpeed.value)
            
    def SetHSSpeed(self, itype, index):
        error = self.dll.SetHSSpeed(itype,index)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        self.hsspeed = index
        return ERROR_CODE[error]
        
    def GetNumberVSSpeeds(self):
        noVSSpeeds = c_int()
        error = self.dll.GetNumberVSSpeeds(byref(noVSSpeeds))
        self.noVSSpeeds = noVSSpeeds.value
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def GetVSSpeed(self):
        VSSpeed = c_float()

        self.VSSpeeds = []

        for i in range(self.noVSSpeeds):
            self.dll.GetVSSpeed(i,byref(VSSpeed))
            self.preVSpeeds.append(VSSpeed.value)

    def SetVSSpeed(self, index):
        error = self.dll.SetVSSpeed(index)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        self.vsspeed = index
        return ERROR_CODE[error] 
    
    def GetNumberPreAmpGains(self):
        noGains = c_int()
        error = self.dll.GetNumberPreAmpGains(byref(noGains))
        self.noGains = noGains.value
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def GetPreAmpGain(self):
        gain = c_float()

        self.preAmpGain = []

        for i in range(self.noGains):
            self.dll.GetPreAmpGain(i,byref(gain))
            self.preAmpGain.append(gain.value)

    def SetPreAmpGain(self, index):
        error = self.dll.SetPreAmpGain(index)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        self.preampgain = index
        return ERROR_CODE[error]

    def SetTriggerMode(self, mode):
        error = self.dll.SetTriggerMode(mode)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def GetStatus(self):
        status = c_int()
        error = self.dll.GetStatus(byref(status))
        self.status = ERROR_CODE[status.value]
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return self.status
        
    def GetSeriesProgress(self):
		acc = c_long()
		series = c_long()
		error = self.dll.GetAcquisitionProgress(byref(acc),byref(series))
		if ERROR_CODE[error] == "DRV_SUCCESS":
			return series.value
		else:
			return None
             
    def GetAccumulationProgress(self):
		acc = c_long()
		series = c_long()
		error = self.dll.GetAcquisitionProgress(byref(acc),byref(series))
		if ERROR_CODE[error] == "DRV_SUCCESS":
			return acc.value
		else:
			return None
        
    def SetFrameTransferMode(self, frameTransfer):
        error = self.dll.SetFrameTransferMode(frameTransfer)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]
        
    def SetShutterEx(self, typ, mode, closingtime, openingtime, extmode):
        error = self.dll.SetShutterEx(typ, mode, closingtime, openingtime, extmode)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]
        
    def SetSpool(self, active, method, path, framebuffersize):
        error = self.dll.SetSpool(active, method, c_char_p(path), framebuffersize)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def SetSingleTrack(self, centre, height):
        error = self.dll.SetSingleTrack(centre, height)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]
    
    def SetDemoReady(self):
        error = self.SetSingleScan()
        error = self.SetTriggerMode(0)
        error = self.SetShutter(1,0,30,30)
        error = self.SetExposureTime(0.01)
        return error
    
    def SetBinning(self,binningmode):
        if (binningmode==1):
            self.SetImage(1,1,1,self.width,1,self.height)
        elif (binningmode==2):
            self.SetImage(2,2,1,self.width,1,self.height)
        elif (binningmode==4):
            self.SetImage(4,4,1,self.width,1,self.height)
        else:
            self.verbose("Binning mode not found")

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
    20095: "DRV_INVALID_TRIGGER_MODE",
    20099: "DRV_BINNING_ERROR",
    20990: "DRV_NOCAMERA",
    20991: "DRV_NOT_SUPPORTED",
    20992: "DRV_NOT_AVAILABLE"
}
