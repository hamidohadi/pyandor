from andor import *
import time
cam = Andor()
cam.SetExposureTime(0.1)
cam.SetSingleScan()

print cam.GetEMGainRange()
print cam.GetEMCCDGain()
print cam.gainRange
print cam.gain
print cam.GetNumberPreAmpGains()
print cam.noGains
cam.GetPreAmpGain()

print cam.preAmpGain
print cam.GetStatus()
print cam.status

#cam.StartAcquisition()

#data = []
#cam.GetAcquiredData(data)
#cam.SaveAsBmp("mine2.bmp")

#print cam.GetTemperature()
#print cam.temperature
##cam.CoolerON()

#print cam.SetTemperature(10)

#while True:
    #print cam.GetTemperature()
    #print cam.temperature
    #time.sleep(2)
    
##cam.ShutDown()
