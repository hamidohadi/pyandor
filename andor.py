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

from ctypes import *
import time
from PIL import Image
import sys

"""Andor class which is meant to provide the Python version of the same
   functions that are defined in the Andor's SDK. Since Python does not
   have pass by reference for immutable variables, some of these variables
   are actually stored in the class instance. For example the temperature,
   gain, gainRange, status etc. are stored in the class. """

class Andor:
    def __init__(self):
        cdll.LoadLibrary("/usr/local/lib/libandor.so")
        self.dll = CDLL("/usr/local/lib/libandor.so")
        self.dll.Initialize("/usr/local/etc/andor")

        cw = c_int()
        ch = c_int()
        self.dll.GetDetector(byref(cw), byref(ch))

        self.width = cw.value
        self.height = cw.value
        self.temperature = None
        self.set_T = None
        self.gain = None
        self.gainRange = None
        self.status = None
        self.verbosity = False
        self.preampgain = 0
    
    def verbose(self, error, function=''):
        if self.verbosity is True:
            print "[%s]: %s" %(function, error)

    def SetVerbose(self, state=True):
        self.verbose = state

    def ShutDown(self):
        error = self.dll.ShutDown()
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def SetReadMode(self, mode):
        error = self.dll.SetReadMode(mode)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def SetAcquisitionMode(self, mode):
        error = self.dll.SetAcquisitionMode(mode)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def SetShutter(self,typ,mode,closingtime,openingtime):
        error = self.dll.SetShutter(typ,mode,closingtime,openingtime)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def SetImage(self,hbin,vbin,hstart,hend,vstart,vend):
        error = self.dll.SetImage(hbin,vbin,hstart,hend,vstart,vend)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def StartAcquisition(self):
        error = self.dll.StartAcquisition()
        self.dll.WaitForAcquisition()
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def GetAcquiredData(self,imageArray):
        dim = self.width * self.height
        cimageArray = c_int * dim
        cimage = cimageArray()
        error = self.dll.GetAcquiredData(pointer(cimage),dim)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)

        for i in range(len(cimage)):
            imageArray.append(cimage[i])

        self.imageArray = imageArray[:]
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def SetExposureTime(self, time):
        error = self.dll.SetExposureTime(c_float(time))
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

    def SaveAsBmp(self, path):
        im=Image.new("RGB",(512,512),"white")
        pix = im.load()

        for i in range(len(self.imageArray)):
            (row, col) = divmod(i,self.width)
            picvalue = int(round(self.imageArray[i]*255.0/65535))
            pix[row,col] = (picvalue,picvalue,picvalue)

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

        im=Image.new("RGB",(512,512),"white")
        pix = im.load()

        maxIntensity = max(self.imageArray)

        for i in range(len(self.imageArray)):
            (row, col) = divmod(i,self.width)
            picvalue = int(round(self.imageArray[i]*255.0/maxIntensity))
            pix[row,col] = (picvalue,picvalue,picvalue)

        im.save(path,"BMP")

    def CoolerON(self):
        error = self.dll.CoolerON()
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def CoolerOFF(self):
        error = self.dll.CoolerOFF()
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def IsCoolerOn(self):
        iCoolerStatus = c_int()
        error = self.dll.IsCoolerOn(byref(iCoolerStatus))
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return iCoolerStatus

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

    def SetEMCCDGain(self, gain):
        error = self.dll.SetEMCCDGain(gain)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def GetEMGainRange(self):
        low = c_int()
        high = c_int()
        error = self.dll.GetEMGainRange(byref(low),byref(high))
        self.gainRange = (low.value, high.value)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
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
        return ERROR_CODE[error]

    def SetOutputAmplifier(self, typ):
        error = self.dll.SetOutputAmplifier(typ)
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

ERROR_CODE = {
    20002: "DRV_SUCCESS",
    20013: "DRV_ERROR_ACK",
    20034: "DRV_TEMP_OFF",
    20035: "DRV_TEMP_NOT_STABILIZED",
    20036: "DRV_TEMP_STABILIZED",
    20037: "DRV_TEMP_NOT_REACHED",
    20038: "DRV_TEMP_OUT_RANGE",
    20039: "DRV_TEMP_NOT_SUPPORTED",
    20040: "DRV_TEMP_DRIFT",
    20066: "DRV_P1INVALID",
    20072: "DRV_ACQUIRING",
    20073: "DRV_IDLE",
    20074: "DRV_TEMPCYCLE",
    20075: "DRV_NOT_INITIALIZED"
}
