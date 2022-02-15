import os
from numpy import *
from anti_qsweepy.drivers import *
from anti_qsweepy.routines.helper_functions import *

Script = "Igor\\SvsI_magnet.py"

#Thermocontroller
Name = "iTC"
Sensor = "SAMP_DB6"
PIDtable = "iTC PID tables\\FMR.txt"
Ttol = 5e-2
HoldTime = 30
Timeout = 1200
Ntrys = 5

tc = Mercury_iTc.TemperatureController('iTC')
tc.SetLoopParam( Sensor,"TSET", 0 )
tc.SetLoopParam( Sensor,"ENAB", "ON" )
tc.close()

#Tlist = [5.,6.,7.,8.,8.2,8.4]
Tlist = [10.,]

try:
	for T in Tlist:
		for n in range(Ntrys):
			try:
				tc = Mercury_iTc.TemperatureController('iTC')
				tc.SetPIDtable( Sensor, PIDtable)
				tc.SetAutoPID( Sensor, True )
				break
			except:
				try:tc.close()
				except: pass	
				if n<(Ntrys-1):
					pass
		tc.setpoint(Sensor, T) 
		WaitForStableT( T, tc.temperature, Sensor, Ttol, HoldTime, tc.heater_value, Timeout)
		if T==0.:
			(T,err) = tc.GetSensorSig(Sensor, "TEMP")
		tc.close()
		os.system("python "+Script+" {:.4f}K".format(T) )
except KeyboardInterrupt: pass