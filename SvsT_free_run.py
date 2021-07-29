from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
import scipy.interpolate as si
import tables
from numpy import *
import time

Data_dir ="E:/Abramov" 
plotting_script = "plot_2d_S"
Tstep_profile  = [[0.,0.1], [3.,0.1], [3.1,2], [350.,2]]
tc_chan_high = "T6"
tc_chan_low = "T5"
T_high_low = 1.6

preset = True
points = 3000

f_cent_span = True
f_cent = 3.2754e9
span = 0.04e9
f_start = 6e9
f_stop = 7e9

bw = 100
power = 0

#na = Agilent_PNA.NetworkAnalyzer('pna')
na = RS_ZNB20.NetworkAnalyzer('ZNB20')
tc = Triton_DR200.TemperatureController('DR200', term_chars = '\n')
###########################################################################
print("VNA scan vs temperature")
path = data_mgmt.default_save_path(Data_dir, name = "SvsT")
print("Saving files to: ",path)

Tstep_func = si.interp1d([x[0] for x in Tstep_profile], [x[1] for x in Tstep_profile])

def get_T():
	Tlow = tc.temperature(tc_chan_low)
	T = tc.temperature(tc_chan_high)
	if T < T_high_low:
		T = Tlow
	return T	

if preset:
	na.num_of_points(points)
	if f_cent_span:
		na.freq_center(f_cent)
		na.freq_span(span)
	else:
		na.freq_start(f_start)
		na.freq_stop(f_stop)
	na.bandwidth(bw)
	na.power(power)

Fna = na.freq_points()
f, d_array, r_array = data_mgmt.extendable_2d(path,Fna, row_descr = "Temperature, K" )
data_mgmt.spawn_plotting_script(path, plotting_script)

na.output('on')
#Sweep
na.soft_trig_arm()
Tlast = 0.
Tstep = 0.
try:
	while(1):
		T = get_T()	
		print("T = {:f} K                       ".format(T), end = '\r')
		if abs(T-Tlast) >= Tstep:
			Tlast = T
			print("Measuring at T = {:f} K...".format(T), end = '\r')
			S = na.read_data()
			d_array.append(S.reshape(1,len(S) ))
			r_array.append( array([T]) )
			f.flush()
		Tstep = Tstep_func(T)
		time.sleep(1)	
except KeyboardInterrupt:
	print( "Interrupted by user                                 " )
	
na.soft_trig_abort()	
na.close()
tc.close()
f.close()	