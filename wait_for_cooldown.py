from anti_qsweepy.drivers import *
import time

tc_chan = "T5"
T_thr = 30e-3
tc = Triton_DR200.TemperatureController('DR200', term_chars = '\n')
print("Waiting for temperature below {:f} K".format(T_thr))
try:
	while(1):
		T = tc.temperature(tc_chan)
		print("T = {:.5f} K            ".format(T), end = '\r')
		if  T <= T_thr:
			break
		time.sleep(1)	
except KeyboardInterrupt:
	print( "Interrupted by user " )
