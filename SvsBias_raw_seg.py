from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.helper_functions import *

import tables
from numpy import *

Data_dir ="E:\Abramov" 
plotting_script = "plot_2d_S"
row_descr = "Voltage, V"

bias_step = 0.1
bias_vals = arange(0, 10, bias_step)
bias_vals = hstack(( bias_vals, arange(10,-10, -bias_step) ))
bias_vals = hstack(( bias_vals, arange(-10,0, bias_step) ))
#bias_vals = hstack(( bias_vals, arange(-10,10, bias_step) ))
#bias_vals = hstack(( bias_vals, arange(10,-10, -bias_step) ))
#bias_vals = hstack(( bias_vals, arange(-10,0, bias_step) ))

bias_range = 10
bias_limit = 100e-6


#Segments = [{'start':100e6, 'stop':200e6, 'points':20000, 'power':-20,'bandwidth':200},	
#			{'start':250e6, 'stop':2e9, 'points':20000, 'power':-20,'bandwidth':500}]
#			{'start':400e6, 'stop':500e6, 'points':1000, 'power':-20,'bandwidth':1e3}]

Segments = [{'start':40e6, 'stop':1.6e9, 'points':20001, 'power':-20,'bandwidth':200},]

na = Agilent_PNA.NetworkAnalyzer('PNA-X')
#na = RS_ZNB20.NetworkAnalyzer('ZNB20')
#bias_source = STS60.BiasSourceByNNDAC("NNDAC")
#bias_source = Keithley_2400.CurrentSource('2400')
bias_source = Keithley_2400.SMU('2400')
#bias_source = Keithley_6221.CurrentSource('GPIB0::10::INSTR')
#bias_source = Keithley_2651.MagnetSupply("NNDAC", rate = 1.)
###########################################################################
print("VNA bias scan")
path = data_mgmt.default_save_path(Data_dir, name = "SvsBias")
print("Saving files to: ",path)

na.seg_tab(Segments)
na.sweep_type("SEGM")

bias_source.source("VOLT")
bias_source.range(bias_range)
bias_source.limit(bias_limit)
	
Fna = na.freq_points()
f, d_array, r_array = data_mgmt.extendable_2d(path, Fna, row_descr = row_descr)
data_mgmt.spawn_plotting_script(path, plotting_script)

na.output('on')
bias_source.output('on')
#Sweep
print( "Parameter range: from {:.3f} to {:.3f}".format( min(bias_vals), max(bias_vals) ))
na.soft_trig_arm()
for bias_val in bias_vals:
	try:
		bias_source.setpoint(bias_val) 
		print("Bias = {:f}".format(bias_val), end = '\r')
		S = na.read_data()
		d_array.append(S.reshape(1,len(S) ))
		r_array.append( array([bias_val]) )
		f.flush()
	except KeyboardInterrupt:
		print( "Interrupted by user" )
		break
bias_source.output('off')		
na.soft_trig_abort()	
f.close()	