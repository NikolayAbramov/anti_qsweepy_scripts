from anti_qsweepy.drivers import *

chan = "SAMP_DB6"
#chan = "JT_CERNOX"
PIDtable = "FMR.txt"
#PIDtable = "JT_3K.txt"

tol = 5e-2						#Temperature setting tolerance
timeout  = 1200					#Max. seconds to wait for stable T within the tolerance
hold_time = 20. 					#Time to prove that T is within the tolerance and stable
T = 10
PID = True

tc = Mercury_iTc.TemperatureController( "iTc", term_chars = '\n' )

if PID:
	tc.SetLoopParam( chan,"ENAB", "ON" )
	tc.SetPIDtable( chan, PIDtable)
	tc.SetAutoPID( chan, True )
tc.setpoint(chan, T)
print("Waiting for setpoint {:f} +- {:f} K".format(T, tol))	
tc.wait_for_stable_T(chan, tol, hold_time, timeout)
tc.close()