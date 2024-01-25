import os
from numpy import *
from anti_qsweepy.drivers import *
from anti_qsweepy.routines.helper_functions import *

Script = "Igor\\SvsI_magnet_sr.py"
#Script = "Igor\\SvsI_magnet.py"

#Thermocontroller
Name = "iTC"
Sensor = "SAMP_DB6"
PIDtable = "iTC PID tables\\FMR1.txt"
Ttol = 5e-2
HoldTime = 30
Timeout = 1200
Ntrys = 5

tc = Mercury_iTc.TemperatureController('iTC')
tc.SetLoopParam( Sensor,"TSET", 0 )
tc.SetLoopParam( Sensor,"ENAB", "ON" )
tc.close()

Tlist = [5.5,6,6.5,7]
#Tlist = [0]
#Tlist = arange(11,25,1)
#Tlist = [13, 16, 19, 22, 25, 28, 31, 34, 38]
#Tlist = [0, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 11]
#Tlist = hstack( (Tlist, arange(7.6,8.,0.1), [7.2,7.4, 6.75, 6.25, 5.75] ) )
#Tlist = [0, arange(1.6,5.0,0.1)]
#Tlist = [7.2,] 

def connect():
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
	return tc

try:
	for T in Tlist:
		tc = connect()
		tc.setpoint(Sensor, T) 
		WaitForStableT( T, tc.temperature, Sensor, Ttol, HoldTime, tc.heater_value, Timeout)
		if T==0.:
			(T,err) = tc.GetSensorSig(Sensor, "TEMP")
		tc.close()
		os.system("python "+Script+" {:.4f}K".format(T) )
except KeyboardInterrupt: pass

tc = connect()
tc.setpoint(Sensor, 0)
tc.close()

