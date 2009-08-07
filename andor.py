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
        self.gain = None
        self.gainRange = None
        self.status = None
    
    def ShutDown(self):
        error = self.dll.ShutDown()
        return ERROR_CODE[error]

    def SetReadMode(self, mode):
        error = self.dll.SetReadMode(mode)
        return ERROR_CODE[error]

    def SetAcquisitionMode(self, mode):
        error = self.dll.SetAcquisitionMode(mode)
        return ERROR_CODE[error]

    def SetShutter(self,typ,mode,closingtime,openingtime):
        error = self.dll.SetShutter(typ,mode,closingtime,openingtime)
        return ERROR_CODE[error]

    def SetImage(self,hbin,vbin,hstart,hend,vstart,vend):
        error = self.dll.SetImage(hbin,vbin,hstart,hend,vstart,vend)
        return ERROR_CODE[error]

    def StartAcquisition(self):
        error = self.dll.StartAcquisition()
        self.dll.WaitForAcquisition()
        return ERROR_CODE[error]

    def GetAcquiredData(self,imageArray):
        dim = self.width * self.height
        cimageArray = c_int * dim
        cimage = cimageArray()
        error = self.dll.GetAcquiredData(pointer(cimage),dim)

        for i in range(len(cimage)):
            imageArray.append(cimage[i])

        self.imageArray = imageArray[:]
        return ERROR_CODE[error]

    def SetExposureTime(self, time):
        error = self.dll.SetExposureTime(c_float(time))
        return ERROR_CODE[error]

    def SetSingleScan(self):
        self.SetReadMode(4)
        self.SetAcquisitionMode(1)
        self.SetImage(1,1,1,self.width,1,self.height)

    def SaveAsBmp(self, path):
        im=Image.new("RGB",(512,512),"white")
        pix = im.load()

        for i in range(len(self.imageArray)):
            (row, col) = divmod(i,self.width)
            picvalue = int(round(self.imageArray[i]*255.0/65535))
            pix[row,col] = (picvalue,picvalue,picvalue)

        im.save(path,"BMP")

    def SetTemperature(self,temperature):
        error = self.dll.SetTemperature(temperature)
        return ERROR_CODE[error]

    def CoolerON(self):
        error = self.dll.CoolerON()
        return ERROR_CODE[error]

    def CoolerOFF(self):
        error = self.dll.CoolerOFF()
        return ERROR_CODE[error]

    def GetTemperature(self):
        ctemperature = c_int()
        error = self.dll.GetTemperature(byref(ctemperature))
        self.temperature = ctemperature.value
        return ERROR_CODE[error]

    def SetTemperature(self,temperature):
        #ctemperature = c_int(temperature)
        #error = self.dll.SetTemperature(byref(ctemperature))
        error = self.dll.SetTemperature(temperature)
        return ERROR_CODE[error]

    def GetEMCCDGain(self):
        gain = c_int()
        error = self.dll.GetEMCCDGain(byref(gain))
        self.gain = gain.value
        return ERROR_CODE[error]

    def SetEMCCDGain(self, gain):
        error = self.dll.SetEMCCDGain(gain)
        return ERROR_CODE[error]

    def GetEMGainRange(self):
        low = c_int()
        high = c_int()
        error = self.dll.GetEMGainRange(byref(low),byref(high))
        self.gainRange = (low.value, high.value)
        return ERROR_CODE[error]

    def GetNumberPreAmpGains(self):
        noGains = c_int()
        error = self.dll.GetNumberPreAmpGains(byref(noGains))
        self.noGains = noGains.value
        return ERROR_CODE[error]

    def GetPreAmpGain(self):
        gain = c_float()

        self.preAmpGain = []

        for i in range(self.noGains):
            self.dll.GetPreAmpGain(i,byref(gain))
            self.preAmpGain.append(gain.value)

    def SetPreAmpGain(self, index):
        error = self.dll.SetPreAmpGain(index)
        return ERROR_CODE[error]

    def SetTriggerMode(self, mode):
        error = self.dll.SetTriggerMode(mode)
        return ERROR_CODE[error]

    def GetStatus(self):
        status = c_int()
        error = self.dll.GetStatus(byref(status))
        self.status = ERROR_CODE[status.value]
        return ERROR_CODE[error]

    def SetOutputAmplifier(self, typ):
        error = self.dll.SetOutputAmplifier(typ)
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
