"""Spectrum alalyzer bias sweep"""

from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.helper_functions import *

import tables
from numpy import *

Data_dir ="D:\Belanovsky" 
plotting_script = "plot_2d"
row_descr = "Current, A"

bias_vals = arange(10.0e-3, 13e-3, 0.01e-3) #9e-6,12e-6, 0.05e-6
#bias_vals = append( bias_vals, arange(4e-3, -0.01e-3, -0.01e-3) )
bias_range = 10e-3
bias_limit = 50

preset = True
Fstart = 4e9
Fstop = 6e9
rbw = 100e3
vbw = 10e3

sa = Keysight_MXA.SpectrumAnalyzer('Keysight_MXA')
sa.instr.timeout=5000000
bias_source = Keithley_6221.CurrentSource('Keithley_6221')
###########################################################################
print("SA bias scan")
path = data_mgmt.default_save_path(Data_dir, name = "Spec_vs_Bias_long_JJ_rbw100kHz_vbw10p0kHz_0p0mA")
print("Saving files to: ",path)

if preset:
	sa.freq_start_stop((Fstart,Fstop))
	sa.rbw(rbw)
	sa.vbw(vbw)

bias_source.range(bias_range)
bias_source.limit(bias_limit)
	
F = sa.freq_points()
f, d_array, r_array = data_mgmt.extendable_2d(path, F, row_descr = row_descr)
data_mgmt.spawn_plotting_script(path, plotting_script)

#zero bias scan
bias_source.output('off')
try:
	bias_source.setpoint(0.0) 
	print("Bias = {:f}".format(0.0), end = '\r')
	S = sa.read_data()
	d_array.append(S.reshape(1,len(S) ))
	r_array.append( array([0.0]) )
	f.flush()
except KeyboardInterrupt:
	print( "Interrupted by user" )

bias_source.output('on')
#Sweep
print( "Parameter range: from {:.3f} to {:.3f}".format( min(bias_vals), max(bias_vals) ))
sa.soft_trig_arm()
for bias_val in bias_vals:
	try:
		bias_source.setpoint(bias_val) 
		print("Bias = {:f}".format(bias_val), end = '\r')
		S = sa.read_data()
		d_array.append(S.reshape(1,len(S) ))
		r_array.append( array([bias_val]) )
		f.flush()
	except KeyboardInterrupt:
		print( "Interrupted by user" )
		break
bias_source.output('off')		
sa.soft_trig_abort()	
f.close()	