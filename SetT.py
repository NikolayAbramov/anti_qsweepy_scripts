from anti_qsweepy.drivers import *
from anti_qsweepy.routines.helper_functions import *

chan = "SAMP_DB6"
#chan = "JT_CERNOX"
PIDtable = "iTC PID tables\\FMR1.txt"
#PIDtable = "JT_3K.txt"

tol = 5e-2						#Temperature setting tolerance
timeout  = 1200					#Max. seconds to wait for stable T within the tolerance
hold_time = 20. 				#Time to prove that T is within the tolerance and stable
T = 0
PID = True

tc = Mercury_iTc.TemperatureController( "iTc" )

if PID:
	tc.SetLoopParam( chan,"ENAB", "ON" )
	tc.SetPIDtable( chan, PIDtable)
	tc.SetAutoPID( chan, True )
tc.setpoint(chan, T)
print("Waiting for setpoint {:f} +- {:f} K".format(T, tol))	
WaitForStableT( T, tc.temperature, chan, tol, hold_time, tc.heater_value, timeout)
tc.close()